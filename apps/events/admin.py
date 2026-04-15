from django.contrib import admin

from .models import HistoricalEvent


@admin.register(HistoricalEvent)
class HistoricalEventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_date_text",
        "source",
        "event_type",
        "scope",
        "imported_from_historyrussia",
        "is_featured",
        "is_published",
        "last_synced_at",
    )
    list_filter = (
        "source",
        "imported_from_historyrussia",
        "is_published",
        "is_featured",
        "event_type",
        "scope",
        "day",
        "month",
        "year",
    )
    search_fields = ("title", "summary", "full_text", "source_url", "canonical_url", "source_uid")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags", "related_materials", "related_tests")
    autocomplete_fields = ("source",)
    actions = ("publish_selected", "unpublish_selected", "reslug_selected", "mark_featured", "mark_not_featured")
    fields = (
        "title",
        "slug",
        "source",
        "source_url",
        "canonical_url",
        "source_domain",
        "summary",
        "full_text",
        "image",
        "image_url_original",
        "day",
        "month",
        "year",
        "display_date_text",
        "event_date_precision",
        "event_type",
        "scope",
        "tags",
        "related_materials",
        "related_tests",
        "is_featured",
        "is_published",
        "imported_from_historyrussia",
        "import_status",
        "source_uid",
        "source_hash",
        "published_date_at_source",
        "first_seen_at",
        "last_synced_at",
        "raw_payload_json",
        "raw_html_fragment",
    )
    readonly_fields = ("source_hash", "first_seen_at", "last_synced_at")

    @admin.action(description="Опубликовать выбранные")
    def publish_selected(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description="Снять с публикации")
    def unpublish_selected(self, request, queryset):
        queryset.update(is_published=False)

    @admin.action(description="Пересоздать slug")
    def reslug_selected(self, request, queryset):
        for event in queryset:
            event.slug = ""
            event.save(update_fields=["slug", "updated_at"])

    @admin.action(description="Отметить как featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Снять отметку featured")
    def mark_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
