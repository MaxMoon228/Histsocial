from django.contrib import admin

from .models import FavoriteSessionItem


@admin.register(FavoriteSessionItem)
class FavoriteSessionItemAdmin(admin.ModelAdmin):
    list_display = ("session_key", "content_type", "object_id", "created_at")
    list_filter = ("content_type",)
    search_fields = ("session_key",)
