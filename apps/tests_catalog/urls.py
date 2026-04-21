from django.urls import path

from . import views

urlpatterns = [
    path("tests/", views.tests_page, name="tests"),
    path("self-check/", views.self_check_page, name="self_check"),
    path("activities/", views.activities_page, name="activities"),
    path("htmx/tests/filter/", views.tests_filter, name="tests_filter"),
    path("htmx/self-check/filter/", views.self_check_filter, name="self_check_filter"),
    path("htmx/activities/filter/", views.activities_filter, name="activities_filter"),
    path("staff/tests/create/", views.staff_test_create, name="staff_test_create"),
    path("staff/tests/<int:pk>/edit/", views.staff_test_edit, name="staff_test_edit"),
    path("staff/tests/<int:pk>/duplicate/", views.staff_test_duplicate, name="staff_test_duplicate"),
    path("staff/tests/<int:pk>/toggle-publish/", views.staff_test_toggle_publish, name="staff_test_toggle_publish"),
    path("staff/tests/<int:pk>/delete/", views.staff_test_delete, name="staff_test_delete"),
]
