from django.shortcuts import render
from django.db.models import Q

from apps.common.choices import DIFFICULTY_CHOICES, EXAM_TYPE_CHOICES, TASK_TYPE_CHOICES
from apps.common.models import Source

from .models import TestItem


def _filtered_tests(request):
    queryset = TestItem.objects.filter(is_published=True).select_related("source").prefetch_related("tags")
    query = request.GET.get("q", "").strip()
    exam_type = request.GET.get("exam_type", "")
    task_type = request.GET.get("task_type", "")
    difficulty = request.GET.get("difficulty", "")
    source = request.GET.get("source", "")
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(short_description__icontains=query))
    if exam_type:
        queryset = queryset.filter(exam_type=exam_type)
    if task_type:
        queryset = queryset.filter(task_type=task_type)
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)
    if source:
        queryset = queryset.filter(source__slug=source)
    return queryset.distinct()


def tests_page(request):
    tests = _filtered_tests(request)
    selected = {
        "q": request.GET.get("q", ""),
        "exam_type": request.GET.get("exam_type", ""),
        "task_type": request.GET.get("task_type", ""),
        "difficulty": request.GET.get("difficulty", ""),
        "source": request.GET.get("source", ""),
    }
    tests_qs = TestItem.objects.filter(is_published=True)
    context = {
        "tests": tests,
        "sources": Source.objects.filter(is_active=True),
        "exam_type_choices": EXAM_TYPE_CHOICES,
        "task_type_choices": TASK_TYPE_CHOICES,
        "difficulty_choices": DIFFICULTY_CHOICES,
        "selected": selected,
        "stats_ege": tests_qs.filter(exam_type="ege").count(),
        "stats_oge": tests_qs.filter(exam_type="oge").count(),
        "stats_trainer": tests_qs.filter(exam_type="school_trainer").count(),
        "total_count": tests.count(),
    }
    return render(request, "tests_catalog/tests.html", context)


def tests_filter(request):
    tests = _filtered_tests(request)
    return render(request, "tests_catalog/partials/tests_grid.html", {"tests": tests, "total_count": tests.count()})
