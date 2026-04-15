from django.contrib import admin

from .models import Material, MaterialAttachment


class MaterialAttachmentInline(admin.TabularInline):
    model = MaterialAttachment
    extra = 1


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "material_kind", "source", "level", "is_published", "is_archived", "sort_order", "updated_at", "updated_by")
    list_filter = ("section", "material_kind", "level", "is_published", "is_archived", "source")
    search_fields = ("title", "short_description", "full_description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    autocomplete_fields = ("source",)
    inlines = [MaterialAttachmentInline]
    actions = ("publish_selected", "unpublish_selected", "archive_selected")

    @admin.action(description="Опубликовать выбранные")
    def publish_selected(self, request, queryset):
        queryset.update(is_published=True, is_archived=False, updated_by=request.user)

    @admin.action(description="Снять с публикации")
    def unpublish_selected(self, request, queryset):
        queryset.update(is_published=False, updated_by=request.user)

    @admin.action(description="Архивировать выбранные")
    def archive_selected(self, request, queryset):
        queryset.update(is_archived=True, is_published=False, updated_by=request.user)


@admin.register(MaterialAttachment)
class MaterialAttachmentAdmin(admin.ModelAdmin):
    list_display = ("title", "material", "attachment_kind", "sort_order")
    list_filter = ("attachment_kind",)
    search_fields = ("title", "material__title")
    autocomplete_fields = ("material",)
