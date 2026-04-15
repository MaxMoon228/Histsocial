from django.urls import path

from . import views

urlpatterns = [
    path("axis/", views.axis_page, name="axis"),
    path("htmx/axis/results/", views.axis_results, name="axis_results"),
    path("htmx/axis/node/<int:pk>/", views.axis_node_detail, name="axis_node_detail"),
    path("staff/axis-nodes/create/", views.staff_axis_node_create, name="staff_axis_node_create"),
    path("staff/axis-nodes/<int:pk>/edit/", views.staff_axis_node_edit, name="staff_axis_node_edit"),
    path("staff/axis-nodes/<int:pk>/duplicate/", views.staff_axis_node_duplicate, name="staff_axis_node_duplicate"),
    path("staff/axis-nodes/<int:pk>/toggle-publish/", views.staff_axis_node_toggle_publish, name="staff_axis_node_toggle_publish"),
    path("staff/axis-nodes/<int:pk>/delete/", views.staff_axis_node_delete, name="staff_axis_node_delete"),
]
