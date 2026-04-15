from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("search/", views.search_results, name="search"),
    path("htmx/search-suggest/", views.search_suggest, name="search_suggest"),
    path("go/<str:content_type>/<int:pk>/", views.external_go, name="external_go"),
    path("health/", views.health, name="health"),
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
]
