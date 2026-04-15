from django.shortcuts import render
from django.http import HttpResponseBadRequest

from apps.axis.models import TimelineNode
from apps.catalog.models import Material
from apps.events.models import HistoricalEvent
from apps.tests_catalog.models import TestItem

from .models import FavoriteSessionItem
from .services import ensure_session_favorites, total_favorites_count

TYPE_MAP = {
    "materials": Material,
    "tests": TestItem,
    "events": HistoricalEvent,
    "topics": TimelineNode,
}


def favorites_page(request):
    favorites = ensure_session_favorites(request)
    active_tab = request.GET.get("tab", "all")
    context = {
        "materials": Material.objects.filter(pk__in=favorites["materials"]),
        "tests": TestItem.objects.filter(pk__in=favorites["tests"]),
        "events": HistoricalEvent.objects.filter(pk__in=favorites["events"]),
        "topics": TimelineNode.objects.filter(pk__in=favorites["topics"]),
        "total_count": total_favorites_count(favorites),
        "active_tab": active_tab,
    }
    return render(request, "favorites/favorites.html", context)


def favorites_toggle(request):
    item_type = request.POST.get("item_type")
    item_id = request.POST.get("item_id")
    if item_type not in TYPE_MAP or not item_id:
        return HttpResponseBadRequest("Invalid payload")
    item_id = int(item_id)
    favorites = ensure_session_favorites(request)
    current = favorites[item_type]
    is_saved = item_id in current
    if is_saved:
        current.remove(item_id)
    else:
        current.append(item_id)
        FavoriteSessionItem.objects.get_or_create(
            session_key=request.session.session_key or "",
            content_type=item_type,
            object_id=item_id,
        )
    request.session.modified = True
    return render(
        request,
        "includes/components/favorite_button.html",
        {
            "item_type": item_type,
            "item_id": item_id,
            "is_saved": not is_saved,
        },
    )


def favorites_count(request):
    favorites = ensure_session_favorites(request)
    return render(request, "includes/components/favorites_counter.html", {"favorites_count": total_favorites_count(favorites)})
