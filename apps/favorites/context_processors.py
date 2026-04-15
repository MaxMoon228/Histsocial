from .services import ensure_session_favorites, total_favorites_count


def favorites_context(request):
    favorites = ensure_session_favorites(request)
    return {
        "favorites_count": total_favorites_count(favorites),
        "favorites_state": favorites,
    }
