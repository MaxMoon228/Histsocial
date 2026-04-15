from django.urls import path

from . import views

urlpatterns = [
    path("world/", views.world, name="world"),
    path("russia/", views.russia, name="russia"),
    path("social/", views.social, name="social"),
    path("htmx/world/filter/", views.world_filter, name="world_filter"),
    path("htmx/russia/filter/", views.russia_filter, name="russia_filter"),
    path("htmx/social/filter/", views.social_filter, name="social_filter"),
    path("staff/materials/create/", views.staff_material_create, name="staff_material_create"),
    path("staff/materials/<int:pk>/edit/", views.staff_material_edit, name="staff_material_edit"),
    path("staff/materials/<int:pk>/duplicate/", views.staff_material_duplicate, name="staff_material_duplicate"),
    path("staff/materials/<int:pk>/archive/", views.staff_material_archive, name="staff_material_archive"),
    path("staff/materials/<int:pk>/delete/", views.staff_material_delete, name="staff_material_delete"),
    path("staff/materials/<int:pk>/toggle-publish/", views.staff_material_toggle_publish, name="staff_material_toggle_publish"),
    path("staff/materials/bulk/", views.staff_material_bulk, name="staff_material_bulk"),
]
