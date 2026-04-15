from django.contrib import admin

from .models import TimelineNode


@admin.register(TimelineNode)
class TimelineNodeAdmin(admin.ModelAdmin):
    list_display = ("title", "scope", "scale", "display_year_text", "position_order", "is_published")
    list_filter = ("scope", "scale", "is_published")
    search_fields = ("title", "subtitle", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    autocomplete_fields = ("linked_event", "linked_material", "linked_test")
