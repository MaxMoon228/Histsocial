from django.conf import settings

FAVORITE_GROUPS = ("materials", "tests", "events", "topics")


def ensure_session_favorites(request):
    fallback = {key: [] for key in FAVORITE_GROUPS}
    try:
        if not request.session.session_key:
            request.session.save()
        favorites = request.session.get(settings.FAVORITES_SESSION_KEY)
        if not favorites:
            favorites = fallback.copy()
            request.session[settings.FAVORITES_SESSION_KEY] = favorites
            request.session.modified = True
        return favorites
    except Exception:
        # Do not crash full page rendering if session backend is temporarily unavailable.
        return fallback


def total_favorites_count(favorites):
    return sum(len(values) for values in favorites.values())
