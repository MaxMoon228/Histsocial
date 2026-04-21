from django.contrib import admin

from .models import HomePageAuthorBlock


@admin.register(HomePageAuthorBlock)
class HomePageAuthorBlockAdmin(admin.ModelAdmin):
    list_display = ("section_label", "title_text", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("section_label", "title_text", "subtitle_text", "description_text")
