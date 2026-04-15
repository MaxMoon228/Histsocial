from django.urls import path

from . import views

urlpatterns = [
    path("calendar/", views.calendar_page, name="calendar"),
    path("htmx/calendar/day/", views.calendar_day, name="calendar_day"),
    path("staff/events/<int:pk>/toggle-publish/", views.staff_event_toggle_publish, name="staff_event_toggle_publish"),
    path("staff/events/create/", views.staff_event_create, name="staff_event_create"),
    path("staff/events/<int:pk>/edit/", views.staff_event_edit, name="staff_event_edit"),
    path("staff/events/<int:pk>/duplicate/", views.staff_event_duplicate, name="staff_event_duplicate"),
    path("staff/events/<int:pk>/delete/", views.staff_event_delete, name="staff_event_delete"),
]
