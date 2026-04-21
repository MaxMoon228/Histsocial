from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.common.choices import LEVEL_CHOICES, MATERIAL_KIND_CHOICES
from apps.common.models import Source, Tag

from .forms import MaterialStaffForm, MaterialQuickActionForm
from .models import Material

RUSSIA_CLASS_FILTERS = {
    "6 класс": [6],
    "7 класс": [7],
    "8 класс": [8],
    "9 класс": [9],
    "10-11 класс": [10, 11],
}

WORLD_CLASS_FILTERS = {
    "6 класс": [6],
    "7 класс": [7],
    "8 класс": [8],
    "9 класс": [9],
    "10 класс": [10],
    "11 класс": [11],
}


def _filtered_materials(section, request):
    queryset = Material.objects.filter(section=section).select_related("source").prefetch_related("tags")
    if request.user.is_staff:
        staff_state = request.GET.get("staff_state", "all")
        if staff_state == "published":
            queryset = queryset.filter(is_published=True, is_archived=False)
        elif staff_state == "draft":
            queryset = queryset.filter(is_published=False, is_archived=False)
        elif staff_state == "archived":
            queryset = queryset.filter(is_archived=True)
        elif staff_state == "no_tags":
            queryset = queryset.filter(tags__isnull=True)
        elif staff_state == "no_cover":
            queryset = queryset.filter(cover_image="")
        elif staff_state == "no_link":
            queryset = queryset.filter(external_url="", primary_file="")
    else:
        queryset = queryset.filter(is_published=True, is_archived=False)
    query = request.GET.get("q", "").strip()
    level = request.GET.get("level", "")
    material_kind = request.GET.get("material_kind", "")
    source = request.GET.get("source", "")
    tag = request.GET.get("tag", "")
    quick = request.GET.get("quick", "").strip()
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(short_description__icontains=query))
    if level:
        queryset = queryset.filter(level=level)
    if material_kind:
        queryset = queryset.filter(material_kind=material_kind)
    if source:
        queryset = queryset.filter(source__slug=source)
    if tag:
        queryset = queryset.filter(tags__slug=tag)
    if quick:
        class_map = {}
        if section == "russia":
            class_map = RUSSIA_CLASS_FILTERS
        elif section == "world":
            class_map = WORLD_CLASS_FILTERS
        if quick in class_map:
            class_filters = Q()
            for class_num in class_map[quick]:
                class_filters |= Q(external_url__contains=f"/{class_num}/")
            queryset = queryset.filter(class_filters)
        elif quick.lower() not in {"все периоды", "все темы"}:
            queryset = queryset.filter(
                Q(title__icontains=quick)
                | Q(short_description__icontains=quick)
                | Q(full_description__icontains=quick)
                | Q(tags__name__icontains=quick)
            )
    return queryset.distinct()


def world(request):
    materials = _filtered_materials("world", request)
    period_tabs = [
        "Все периоды",
        "6 класс",
        "7 класс",
        "8 класс",
        "9 класс",
        "10 класс",
        "11 класс",
    ]
    selected = {
        "q": request.GET.get("q", ""),
        "level": request.GET.get("level", ""),
        "material_kind": request.GET.get("material_kind", ""),
        "source": request.GET.get("source", ""),
        "tag": request.GET.get("tag", ""),
        "quick": request.GET.get("quick", ""),
        "staff_state": request.GET.get("staff_state", "all"),
    }
    context = {
        "section_name": "Всеобщая история",
        "section_slug": "world",
        "materials": materials,
        "sources": Source.objects.filter(is_active=True),
        "tags": Tag.objects.filter(tag_type__in=["topic", "period", "era"]),
        "level_choices": LEVEL_CHOICES,
        "material_kind_choices": MATERIAL_KIND_CHOICES,
        "period_tabs": period_tabs,
        "selected": selected,
        "total_count": materials.count(),
        "staff_mode": request.user.is_staff,
        "section_default": "world",
    }
    return render(request, "catalog/world.html", context)


def world_filter(request):
    materials = _filtered_materials("world", request)
    return render(request, "catalog/partials/materials_grid.html", {"materials": materials, "total_count": materials.count()})


def russia(request):
    materials = _filtered_materials("russia", request)
    period_tabs = [
        "Все периоды",
        "6 класс",
        "7 класс",
        "8 класс",
        "9 класс",
        "10-11 класс",
    ]
    selected = {
        "q": request.GET.get("q", ""),
        "level": request.GET.get("level", ""),
        "source": request.GET.get("source", ""),
        "tag": request.GET.get("tag", ""),
        "quick": request.GET.get("quick", ""),
        "staff_state": request.GET.get("staff_state", "all"),
    }
    context = {
        "section_name": "История России",
        "section_slug": "russia",
        "materials": materials,
        "sources": Source.objects.filter(is_active=True),
        "tags": Tag.objects.filter(tag_type__in=["topic", "period", "era"]),
        "level_choices": LEVEL_CHOICES,
        "period_tabs": period_tabs,
        "selected": selected,
        "total_count": materials.count(),
        "staff_mode": request.user.is_staff,
        "section_default": "russia",
    }
    return render(request, "catalog/russia.html", context)


def russia_filter(request):
    materials = _filtered_materials("russia", request)
    return render(request, "catalog/partials/materials_grid.html", {"materials": materials, "total_count": materials.count()})


def social(request):
    materials = _filtered_materials("social", request)
    categories = [
        "Все темы",
        "Человек и общество",
        "Экономика",
        "Социальные отношения",
        "Политика",
        "Право",
        "Духовная культура",
        "ЕГЭ",
        "ОГЭ",
    ]
    quick_topics = ["Экономика", "Право", "Политика", "Социальные отношения"]
    selected = {
        "q": request.GET.get("q", ""),
        "level": request.GET.get("level", ""),
        "material_kind": request.GET.get("material_kind", ""),
        "source": request.GET.get("source", ""),
        "tag": request.GET.get("tag", ""),
        "quick": request.GET.get("quick", ""),
        "staff_state": request.GET.get("staff_state", "all"),
    }
    context = {
        "materials": materials,
        "sources": Source.objects.filter(is_active=True),
        "tags": Tag.objects.filter(tag_type__in=["topic", "period", "era"]),
        "level_choices": LEVEL_CHOICES,
        "material_kind_choices": MATERIAL_KIND_CHOICES,
        "selected": selected,
        "categories": categories,
        "quick_topics": quick_topics,
        "total_count": materials.count(),
        "staff_mode": request.user.is_staff,
        "section_default": "social",
    }
    return render(request, "catalog/social.html", context)


def social_filter(request):
    materials = _filtered_materials("social", request)
    return render(request, "catalog/partials/materials_grid.html", {"materials": materials, "total_count": materials.count()})


def _is_staff(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(_is_staff)
def staff_material_create(request):
    section = request.GET.get("section") or request.POST.get("section") or "world"
    material = Material(section=section)
    return _staff_material_form_response(request, material, is_create=True)


@login_required
@user_passes_test(_is_staff)
def staff_material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return _staff_material_form_response(request, material, is_create=False)


def _staff_material_form_response(request, material, is_create):
    if request.method == "POST":
        form = MaterialStaffForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            with transaction.atomic():
                saved = form.save(commit=False)
                saved.updated_by = request.user
                saved.save()
                form.save_m2m()
                _save_attachments(request, saved)
            response = render(
                request,
                "catalog/staff/partials/editor_success.html",
                {"material": saved, "is_create": is_create},
            )
            response["HX-Trigger"] = "material-updated"
            return response
        return render(
            request,
            "catalog/staff/partials/material_form.html",
            {"form": form, "material": material, "is_create": is_create},
        )
    form = MaterialStaffForm(instance=material, initial={"section": material.section or request.GET.get("section", "world")})
    return render(request, "catalog/staff/partials/material_form.html", {"form": form, "material": material, "is_create": is_create})


def _save_attachments(request, material):
    for attachment in material.attachments.all():
        if request.POST.get(f"attachment_delete_{attachment.id}") == "1":
            attachment.delete()
            continue
        attachment.title = request.POST.get(f"attachment_title_{attachment.id}", attachment.title)
        attachment.external_url = request.POST.get(f"attachment_url_{attachment.id}", attachment.external_url)
        attachment.attachment_kind = request.POST.get(f"attachment_kind_{attachment.id}", attachment.attachment_kind)
        try:
            attachment.sort_order = int(request.POST.get(f"attachment_sort_{attachment.id}", attachment.sort_order))
        except (TypeError, ValueError):
            pass
        new_file = request.FILES.get(f"attachment_file_{attachment.id}")
        if new_file:
            attachment.file = new_file
        attachment.save()

    new_title = request.POST.get("new_attachment_title", "").strip()
    new_url = request.POST.get("new_attachment_url", "").strip()
    new_kind = request.POST.get("new_attachment_kind", "other")
    new_file = request.FILES.get("new_attachment_file")
    if new_title or new_url or new_file:
        material.attachments.create(
            title=new_title or "Вложение",
            external_url=new_url,
            attachment_kind=new_kind,
            file=new_file,
            sort_order=material.attachments.count() + 1,
        )


@login_required
@user_passes_test(_is_staff)
def staff_material_duplicate(request, pk):
    original = get_object_or_404(Material, pk=pk)
    clone = Material.objects.get(pk=original.pk)
    clone.pk = None
    clone.slug = f"{original.slug}-copy-{Material.objects.count() + 1}"
    clone.title = f"{original.title} (копия)"
    clone.is_published = False
    clone.is_archived = False
    clone.updated_by = request.user
    clone.save()
    clone.tags.set(original.tags.all())
    for attachment in original.attachments.all():
        attachment.pk = None
        attachment.material = clone
        attachment.save()
    response = HttpResponse("ok")
    response["HX-Trigger"] = "material-updated"
    return response


@login_required
@user_passes_test(_is_staff)
def staff_material_archive(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.is_archived = True
    material.is_published = False
    material.updated_by = request.user
    material.save(update_fields=["is_archived", "is_published", "updated_by", "updated_at"])
    response = HttpResponse("ok")
    response["HX-Trigger"] = "material-updated"
    return response


@login_required
@user_passes_test(_is_staff)
def staff_material_toggle_publish(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.is_published = not material.is_published
    if material.is_published:
        material.is_archived = False
    material.updated_by = request.user
    material.save(update_fields=["is_published", "is_archived", "updated_by", "updated_at"])
    response = HttpResponse("ok")
    response["HX-Trigger"] = "material-updated"
    return response


@login_required
@user_passes_test(_is_staff)
def staff_material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.delete()
    response = HttpResponse("ok")
    response["HX-Trigger"] = "material-updated"
    return response


@login_required
@user_passes_test(_is_staff)
def staff_material_bulk(request):
    form = MaterialQuickActionForm(request.POST)
    if not form.is_valid():
        raise Http404
    ids = [int(item) for item in form.cleaned_data["ids"].split(",") if item.strip().isdigit()]
    queryset = Material.objects.filter(id__in=ids)
    action = form.cleaned_data["action"]
    if action == "publish":
        queryset.update(is_published=True, is_archived=False, updated_by=request.user)
    elif action == "unpublish":
        queryset.update(is_published=False, updated_by=request.user)
    elif action == "archive":
        queryset.update(is_archived=True, is_published=False, updated_by=request.user)
    elif action == "delete":
        queryset.delete()
    response = HttpResponse("ok")
    response["HX-Trigger"] = "material-updated"
    return response
