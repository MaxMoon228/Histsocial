from django.contrib import admin
from .models import ExternalClickLog, SearchQueryLog, Source, Tag


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "source_type", "is_active", "sort_order")
    list_filter = ("source_type", "is_active")
    search_fields = ("name", "domain")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "tag_type", "is_featured", "sort_order")
    list_filter = ("tag_type", "is_featured")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(SearchQueryLog)
class SearchQueryLogAdmin(admin.ModelAdmin):
    list_display = ("query", "session_key", "page_context", "created_at")
    list_filter = ("page_context",)
    search_fields = ("query", "session_key")
    readonly_fields = ("created_at",)


@admin.register(ExternalClickLog)
class ExternalClickLogAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "target_url", "referrer_path", "created_at")
    search_fields = ("target_url", "session_key", "referrer_path")
    readonly_fields = ("created_at",)
