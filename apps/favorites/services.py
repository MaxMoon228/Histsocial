from django.conf import settings

FAVORITE_GROUPS = ("materials", "tests", "events", "topics")


def _normalized_favorites(raw_favorites):
    """Return a safe favorites mapping regardless of broken session payloads."""
    fallback = {key: [] for key in FAVORITE_GROUPS}
    if not isinstance(raw_favorites, dict):
        return fallback

    normalized = {}
    for group in FAVORITE_GROUPS:
        values = raw_favorites.get(group, [])
        if isinstance(values, (list, tuple, set)):
            normalized[group] = [item for item in values if isinstance(item, int)]
        else:
            normalized[group] = []
    return normalized


def ensure_session_favorites(request):
    fallback = {key: [] for key in FAVORITE_GROUPS}
    try:
        session = getattr(request, "session", None)
        if session is None:
            return fallback
        favorites = session.get(settings.FAVORITES_SESSION_KEY)
        if not favorites:
            # Do not force session writes during page render.
            favorites = fallback.copy()
        return _normalized_favorites(favorites)
    except Exception:
        # Do not crash full page rendering if session backend is temporarily unavailable.
        return fallback


def total_favorites_count(favorites):
    safe_favorites = _normalized_favorites(favorites)
    return sum(len(values) for values in safe_favorites.values())
