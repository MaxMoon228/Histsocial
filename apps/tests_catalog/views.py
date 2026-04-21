from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.common.choices import DIFFICULTY_CHOICES, EXAM_TYPE_CHOICES, TASK_TYPE_CHOICES
from apps.common.models import Source

from .forms import TestItemStaffForm
from .models import TestItem


def _filtered_tests(request, section="testing"):
    queryset = TestItem.objects.filter(catalog_section=section).select_related("source").prefetch_related("tags")
    if request.user.is_staff:
        staff_state = request.GET.get("staff_state", "all")
        if staff_state == "published":
            queryset = queryset.filter(is_published=True)
        elif staff_state == "draft":
            queryset = queryset.filter(is_published=False)
        elif staff_state == "no_tags":
            queryset = queryset.filter(tags__isnull=True)
        elif staff_state == "no_cover":
            queryset = queryset.filter(cover_image="")
        elif staff_state == "no_link":
            queryset = queryset.filter(external_url="", primary_file="")
    else:
        queryset = queryset.filter(is_published=True)
    query = request.GET.get("q", "").strip()
    exam_type = request.GET.get("exam_type", "")
    task_type = request.GET.get("task_type", "")
    difficulty = request.GET.get("difficulty", "")
    source = request.GET.get("source", "")
    subject = request.GET.get("subject", "")
    history_subsection = request.GET.get("history_subsection", "")
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(short_description__icontains=query))
    if exam_type and section != "activities":
        queryset = queryset.filter(exam_type=exam_type)
    if task_type and section != "activities":
        queryset = queryset.filter(task_type=task_type)
    if difficulty and section != "activities":
        queryset = queryset.filter(difficulty=difficulty)
    if source:
        queryset = queryset.filter(source__slug=source)
    if subject and section != "activities":
        queryset = queryset.filter(subject=subject)
    if history_subsection and section != "activities" and (subject == "history" or not subject):
        queryset = queryset.filter(subject="history", history_subsection=history_subsection)
    return queryset.distinct()


def _catalog_page(request, section, title, description):
    tests = _filtered_tests(request, section=section)
    selected = {
        "q": request.GET.get("q", ""),
        "exam_type": request.GET.get("exam_type", ""),
        "task_type": request.GET.get("task_type", ""),
        "difficulty": request.GET.get("difficulty", ""),
        "source": request.GET.get("source", ""),
        "subject": request.GET.get("subject", ""),
        "history_subsection": request.GET.get("history_subsection", ""),
        "staff_state": request.GET.get("staff_state", "all"),
    }
    tests_qs = TestItem.objects.filter(is_published=True, catalog_section=section)
    context = {
        "tests": tests,
        "sources": Source.objects.filter(is_active=True),
        "exam_type_choices": EXAM_TYPE_CHOICES,
        "task_type_choices": TASK_TYPE_CHOICES,
        "difficulty_choices": DIFFICULTY_CHOICES,
        "subject_choices": [("history", "История"), ("social", "Обществознание")],
        "history_subsections": [("xvii", "История 17 века"), ("xix", "История 19 века")],
        "selected": selected,
        "catalog_section": section,
        "section_title": title,
        "section_description": description,
        "staff_mode": request.user.is_staff,
        "stats_ege": tests_qs.filter(exam_type="ege").count(),
        "stats_oge": tests_qs.filter(exam_type="oge").count(),
        "stats_trainer": tests_qs.filter(exam_type="school_trainer").count(),
        "total_count": tests.count(),
        "is_activities": section == "activities",
    }
    return render(request, "tests_catalog/tests.html", context)


def tests_page(request):
    return _catalog_page(request, "testing", "Тестирования", "Подготовка к ОГЭ, ЕГЭ, тренажеры и проверка знаний")


def self_check_page(request):
    return _catalog_page(
        request,
        "self_check",
        "Викторины",
        "После того как вы изучили определенную тему, предлагаем вам проверить себя и ответить на вопросы нашей викторины",
    )


def activities_page(request):
    return _catalog_page(
        request,
        "activities",
        "Мероприятия",
        "Подборка презентаций, форумов и активностей для дополнительной подготовки.",
    )


def tests_filter(request):
    tests = _filtered_tests(request, section="testing")
    return render(request, "tests_catalog/partials/tests_grid.html", {"tests": tests, "total_count": tests.count()})


def self_check_filter(request):
    tests = _filtered_tests(request, section="self_check")
    return render(request, "tests_catalog/partials/tests_grid.html", {"tests": tests, "total_count": tests.count()})


def activities_filter(request):
    tests = _filtered_tests(request, section="activities")
    return render(request, "tests_catalog/partials/tests_grid.html", {"tests": tests, "total_count": tests.count()})


def _is_staff(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(_is_staff)
def staff_test_create(request):
    section = request.GET.get("mode") or request.POST.get("catalog_section") or "testing"
    test = TestItem(catalog_section=section)
    return _staff_test_form_response(request, test, is_create=True)


@login_required
@user_passes_test(_is_staff)
def staff_test_edit(request, pk):
    test = get_object_or_404(TestItem, pk=pk)
    return _staff_test_form_response(request, test, is_create=False)


def _staff_test_form_response(request, test, is_create):
    if request.method == "POST":
        form = TestItemStaffForm(request.POST, request.FILES, instance=test)
        if form.is_valid():
            with transaction.atomic():
                saved = form.save()
            response = render(
                request,
                "tests_catalog/staff/partials/editor_success.html",
                {"test": saved, "is_create": is_create},
            )
            response["HX-Trigger"] = "staff-updated"
            return response
        return render(
            request,
            "tests_catalog/staff/partials/test_form.html",
            {"form": form, "test": test, "is_create": is_create, "is_activities": test.catalog_section == "activities"},
        )
    form = TestItemStaffForm(instance=test)
    return render(
        request,
        "tests_catalog/staff/partials/test_form.html",
        {"form": form, "test": test, "is_create": is_create, "is_activities": test.catalog_section == "activities"},
    )


@login_required
@user_passes_test(_is_staff)
def staff_test_duplicate(request, pk):
    test = get_object_or_404(TestItem, pk=pk)
    clone = TestItem.objects.get(pk=test.pk)
    clone.pk = None
    clone.slug = ""
    clone.title = f"{test.title} (копия)"
    clone.is_published = False
    clone.save()
    clone.tags.set(test.tags.all())
    clone.related_materials.set(test.related_materials.all())
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response


@login_required
@user_passes_test(_is_staff)
def staff_test_toggle_publish(request, pk):
    test = get_object_or_404(TestItem, pk=pk)
    test.is_published = not test.is_published
    test.save(update_fields=["is_published", "updated_at"])
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response


@login_required
@user_passes_test(_is_staff)
def staff_test_delete(request, pk):
    test = get_object_or_404(TestItem, pk=pk)
    test.delete()
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response
