import calendar
from datetime import date

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .forms import HistoricalEventStaffForm
from .models import HistoricalEvent

CALENDAR_YEAR = 2026


def _get_selected_month(request):
    raw = request.GET.get("month")
    try:
        month = int(raw or date.today().month)
    except (TypeError, ValueError):
        month = date.today().month
    return min(12, max(1, month))


def _get_selected_day(request, selected_month):
    raw_day = request.GET.get("day")
    max_day = calendar.monthrange(CALENDAR_YEAR, selected_month)[1]
    try:
        day = int(raw_day or date.today().day)
    except (TypeError, ValueError):
        day = date.today().day
    return min(max_day, max(1, day))


def _base_events_queryset(request):
    imported_exists = HistoricalEvent.objects.filter(imported_from_historyrussia=True).exists()
    if imported_exists:
        events = HistoricalEvent.objects.filter(
            is_published=True,
            imported_from_historyrussia=True,
            source_url__contains="/sobytiya/den-v-istorii/",
        ).exclude(source_url__endswith="/sobytiya/den-v-istorii.html").select_related("source")
    else:
        events = HistoricalEvent.objects.filter(is_published=True).select_related("source")
    if request.user.is_staff:
        # Staff can moderate unpublished imported events directly from calendar feed.
        include_hidden = request.GET.get("show_hidden", "")
        if include_hidden == "1":
            if imported_exists:
                events = HistoricalEvent.objects.filter(
                    imported_from_historyrussia=True,
                    source_url__contains="/sobytiya/den-v-istorii/",
                ).exclude(source_url__endswith="/sobytiya/den-v-istorii.html").select_related("source")
            else:
                events = HistoricalEvent.objects.all().select_related("source")
    return events


def _month_name_ru(month_number):
    names = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
    }
    return names.get(month_number, calendar.month_name[month_number])


def calendar_page(request):
    selected_month = _get_selected_month(request)
    selected_day = _get_selected_day(request, selected_month)
    today = date.today()
    all_events = _base_events_queryset(request)
    events = all_events.filter(month=selected_month, day=selected_day).order_by("year", "title")
    imported_exists = HistoricalEvent.objects.filter(imported_from_historyrussia=True).exists()
    days_with_events = set(all_events.filter(month=selected_month).values_list("day", flat=True))
    prev_month = selected_month - 1 if selected_month > 1 else None
    next_month = selected_month + 1 if selected_month < 12 else None
    selected_label = f"{selected_day} {_month_name_ru(selected_month).lower()}"
    is_today_selected = selected_month == today.month and selected_day == today.day and CALENDAR_YEAR == today.year
    context = {
        "calendar_year": CALENDAR_YEAR,
        "selected_month": selected_month,
        "selected_day": selected_day,
        "prev_month": prev_month,
        "next_month": next_month,
        "today_day": today.day,
        "today_month": today.month,
        "selected_label": selected_label,
        "is_today_selected": is_today_selected,
        "month_days": calendar.monthcalendar(CALENDAR_YEAR, selected_month),
        "month_name": _month_name_ru(selected_month),
        "days_with_events": days_with_events,
        "events": events,
        "imported_exists": imported_exists,
    }
    return render(request, "events/calendar.html", context)


def calendar_day(request):
    selected_month = _get_selected_month(request)
    selected_day = _get_selected_day(request, selected_month)
    queryset = _base_events_queryset(request).filter(month=selected_month, day=selected_day).order_by("year", "title")
    return render(
        request,
        "events/partials/event_list.html",
        {"events": queryset[:30]},
    )


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_event_toggle_publish(request, pk):
    event = get_object_or_404(HistoricalEvent, pk=pk)
    event.is_published = not event.is_published
    event.save(update_fields=["is_published", "updated_at"])
    return render(request, "includes/components/event_card.html", {"event": event})


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_event_create(request):
    event = HistoricalEvent()
    return _staff_event_form_response(request, event, is_create=True)


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_event_edit(request, pk):
    event = get_object_or_404(HistoricalEvent, pk=pk)
    return _staff_event_form_response(request, event, is_create=False)


def _staff_event_form_response(request, event: HistoricalEvent, is_create: bool):
    if request.method == "POST":
        form = HistoricalEventStaffForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            with transaction.atomic():
                saved = form.save()
            response = render(
                request,
                "events/staff/partials/editor_success.html",
                {"event": saved, "is_create": is_create},
            )
            response["HX-Trigger"] = "staff-updated"
            return response
        return render(
            request,
            "events/staff/partials/event_form.html",
            {"form": form, "event": event, "is_create": is_create},
        )

    form = HistoricalEventStaffForm(instance=event)
    return render(
        request,
        "events/staff/partials/event_form.html",
        {"form": form, "event": event, "is_create": is_create},
    )


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_event_duplicate(request, pk):
    event = get_object_or_404(HistoricalEvent, pk=pk)
    clone = HistoricalEvent.objects.get(pk=event.pk)
    clone.pk = None
    clone.slug = ""
    clone.title = f"{event.title} (копия)"
    clone.is_published = False
    clone.save()
    clone.tags.set(event.tags.all())
    clone.related_materials.set(event.related_materials.all())
    clone.related_tests.set(event.related_tests.all())
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response


@login_required
@user_passes_test(lambda user: user.is_staff)
def staff_event_delete(request, pk):
    event = get_object_or_404(HistoricalEvent, pk=pk)
    event.delete()
    response = HttpResponse("ok")
    response["HX-Trigger"] = "staff-updated"
    return response
