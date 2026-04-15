from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.catalog.models import Material
from apps.tests_catalog.models import TestItem

from .forms import TimelineNodeStaffForm
from .models import TimelineNode


def axis_page(request):
    nodes = _query_nodes(request)
    active_node = nodes.first()
    return render(
        request,
        "axis/axis.html",
        {
            "nodes": nodes,
            "active_node": active_node,
            "active_node_context": _build_node_context(active_node) if active_node else None,
            "total_count": nodes.count(),
            "selected_scope": request.GET.get("scope", "russia"),
            "selected_scale": request.GET.get("scale", "year"),
            "selected_q": request.GET.get("q", ""),
        },
    )


def _query_nodes(request):
    scope = request.GET.get("scope", "russia")
    scale = request.GET.get("scale", "year")
    query = request.GET.get("q", "").strip()
    nodes = TimelineNode.objects.filter(is_published=True)
    if scope and scope != "both":
        nodes = nodes.filter(Q(scope=scope) | Q(scope="both"))
    if scale:
        nodes = nodes.filter(scale=scale)
    if query:
        nodes = nodes.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return nodes


def axis_results(request):
    nodes = _query_nodes(request)
    active_node = nodes.first()
    return render(request, "axis/partials/timeline.html", {"nodes": nodes, "active_node_id": active_node.id if active_node else None})


def axis_node_detail(request, pk):
    node = TimelineNode.objects.filter(is_published=True).select_related("linked_event", "linked_material", "linked_test").prefetch_related("tags").filter(pk=pk).first()
    if not node:
        return render(request, "axis/partials/node_detail.html", {"node": None, "materials": [], "tests": []})
    context = _build_node_context(node)
    context["node"] = node
    return render(request, "axis/partials/node_detail.html", context)


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_axis_node_create(request):
    node = TimelineNode()
    return _staff_axis_node_form_response(request, node, is_create=True)


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_axis_node_edit(request, pk):
    node = get_object_or_404(TimelineNode, pk=pk)
    return _staff_axis_node_form_response(request, node, is_create=False)


def _staff_axis_node_form_response(request, node: TimelineNode, is_create: bool):
    if request.method == "POST":
        form = TimelineNodeStaffForm(request.POST, instance=node)
        if form.is_valid():
            with transaction.atomic():
                saved = form.save()
            response = render(
                request,
                "axis/staff/partials/editor_success.html",
                {"node": saved, "is_create": is_create},
            )
            response["HX-Trigger"] = "staff-updated"
            return response
        return render(
            request,
            "axis/staff/partials/node_form.html",
            {"form": form, "node": node, "is_create": is_create},
            status=422,
        )
    form = TimelineNodeStaffForm(instance=node)
    return render(
        request,
        "axis/staff/partials/node_form.html",
        {"form": form, "node": node, "is_create": is_create},
    )


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_axis_node_duplicate(request, pk):
    node = get_object_or_404(TimelineNode, pk=pk)
    clone = TimelineNode.objects.get(pk=node.pk)
    clone.pk = None
    clone.slug = ""
    clone.title = f"{node.title} (копия)"
    clone.is_published = False
    clone.save()
    clone.tags.set(node.tags.all())
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_axis_node_toggle_publish(request, pk):
    node = get_object_or_404(TimelineNode, pk=pk)
    node.is_published = not node.is_published
    node.save(update_fields=["is_published", "updated_at"])
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_axis_node_delete(request, pk):
    node = get_object_or_404(TimelineNode, pk=pk)
    node.delete()
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response


def _build_node_context(node):
    material_ids = []
    test_ids = []

    materials = []
    tests = []

    if node.linked_material and node.linked_material.is_published:
        materials.append(node.linked_material)
        material_ids.append(node.linked_material.id)
    if node.linked_test and node.linked_test.is_published:
        tests.append(node.linked_test)
        test_ids.append(node.linked_test.id)
    if node.linked_event:
        for material in node.linked_event.related_materials.filter(is_published=True)[:3]:
            if material.id not in material_ids:
                materials.append(material)
                material_ids.append(material.id)
        for test in node.linked_event.related_tests.filter(is_published=True)[:3]:
            if test.id not in test_ids:
                tests.append(test)
                test_ids.append(test.id)

    token = ""
    for part in node.title.replace("-", " ").replace("—", " ").split():
        if len(part) > 3:
            token = part
            break

    if len(materials) < 3:
        related_materials = Material.objects.filter(is_published=True)
        if token:
            related_materials = related_materials.filter(Q(title__icontains=token) | Q(short_description__icontains=token))
        related_materials = related_materials.exclude(id__in=material_ids)[: 3 - len(materials)]
        materials.extend(list(related_materials))

    if len(tests) < 3:
        related_tests = TestItem.objects.filter(is_published=True)
        if token:
            related_tests = related_tests.filter(Q(title__icontains=token) | Q(short_description__icontains=token))
        related_tests = related_tests.exclude(id__in=test_ids)[: 3 - len(tests)]
        tests.extend(list(related_tests))

    tags = list(node.tags.values_list("name", flat=True)[:6])
    if not tags and node.linked_event:
        tags = list(node.linked_event.tags.values_list("name", flat=True)[:6])

    period_left = f"{node.start_year}" if not node.end_year else f"{node.start_year}-{node.end_year}"
    period_right = node.linked_event.year if node.linked_event and node.linked_event.year else node.start_year + 100

    return {
        "materials": materials,
        "tests": tests,
        "related_tags": tags,
        "period_left": period_left,
        "period_right": period_right,
        "materials_count": len(materials),
        "tests_count": len(tests),
        "persons_count": max(1, len(tags)),
    }
