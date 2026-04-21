from django.contrib import admin

from .models import TestItem


@admin.register(TestItem)
class TestItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "catalog_section",
        "subject",
        "history_subsection",
        "exam_type",
        "task_type",
        "difficulty",
        "source",
        "is_published",
        "sort_order",
    )
    list_filter = ("catalog_section", "subject", "history_subsection", "exam_type", "task_type", "difficulty", "is_published", "source")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags", "related_materials")
    autocomplete_fields = ("source",)
