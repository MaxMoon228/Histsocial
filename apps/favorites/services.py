from django.conf import settings

FAVORITE_GROUPS = ("materials", "tests", "events", "topics")


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
        return favorites
    except Exception:
        # Do not crash full page rendering if session backend is temporarily unavailable.
        return fallback


def total_favorites_count(favorites):
    return sum(len(values) for values in favorites.values())
