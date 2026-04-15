import calendar
from datetime import date
from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .forms import HistoricalEventStaffForm
from .models import HistoricalEvent


def _get_selected_date(request):
    year = int(request.GET.get("year", date.today().year) or date.today().year)
    month = int(request.GET.get("month", date.today().month) or date.today().month)
    day = int(request.GET.get("day", date.today().day) or date.today().day)
    return date(year, month, day)


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


def _apply_filters(queryset, selected, mode, scope, event_type):
    if scope:
        queryset = queryset.filter(scope=scope)
    if event_type:
        queryset = queryset.filter(event_type=event_type)

    if mode == "week":
        week_days = [selected + timedelta(days=delta) for delta in range(-3, 4)]
        day_filters = Q()
        for day_item in week_days:
            day_filters |= Q(month=day_item.month, day=day_item.day)
        queryset = queryset.filter(day_filters)
    elif mode == "month":
        queryset = queryset.filter(month=selected.month)
    else:
        queryset = queryset.filter(month=selected.month, day=selected.day)

    return queryset.order_by("month", "day", "year", "title")


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
    selected = _get_selected_date(request)
    mode = request.GET.get("mode", "today")
    scope = request.GET.get("scope", "")
    event_type = request.GET.get("event_type", "")

    all_events = _base_events_queryset(request)
    events = _apply_filters(all_events, selected, mode, scope, event_type)
    imported_exists = HistoricalEvent.objects.filter(imported_from_historyrussia=True).exists()
    if not events.exists():
        events = _base_events_queryset(request).order_by("-last_synced_at", "-updated_at", "month", "day")[:30]
    context = {
        "selected_date": selected,
        "month_days": calendar.monthcalendar(selected.year, selected.month),
        "month_name": _month_name_ru(selected.month),
        "events": events,
        "mode": mode,
        "scope": scope,
        "event_type": event_type,
        "imported_exists": imported_exists,
    }
    return render(request, "events/calendar.html", context)


def calendar_day(request):
    selected = _get_selected_date(request)
    mode = request.GET.get("mode", "today")
    scope = request.GET.get("scope", "")
    event_type = request.GET.get("event_type", "")
    queryset = _apply_filters(_base_events_queryset(request), selected, mode, scope, event_type)
    if not queryset.exists():
        queryset = _base_events_queryset(request).order_by("-last_synced_at", "-updated_at", "month", "day")
    return render(
        request,
        "events/partials/event_list.html",
        {"events": queryset[:30], "selected_date": selected, "mode": mode},
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
            status=422,
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
