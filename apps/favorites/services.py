from django.conf import settings

FAVORITE_GROUPS = ("materials", "tests", "events", "topics")


def ensure_session_favorites(request):
    if not request.session.session_key:
        request.session.save()
    favorites = request.session.get(settings.FAVORITES_SESSION_KEY)
    if not favorites:
        favorites = {key: [] for key in FAVORITE_GROUPS}
        request.session[settings.FAVORITES_SESSION_KEY] = favorites
        request.session.modified = True
    return favorites


def total_favorites_count(favorites):
    return sum(len(values) for values in favorites.values())
