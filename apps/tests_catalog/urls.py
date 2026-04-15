from django.urls import path

from . import views

urlpatterns = [
    path("tests/", views.tests_page, name="tests"),
    path("htmx/tests/filter/", views.tests_filter, name="tests_filter"),
]
