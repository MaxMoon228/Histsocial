from django.urls import path

from . import views

urlpatterns = [
    path("favorites/", views.favorites_page, name="favorites"),
    path("htmx/favorites/toggle/", views.favorites_toggle, name="favorites_toggle"),
    path("htmx/favorites/count/", views.favorites_count, name="favorites_count"),
]
