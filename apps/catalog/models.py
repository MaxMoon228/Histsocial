from django.db import models
from django.conf import settings
from django.utils.text import slugify

from apps.common.choices import (
    ATTACHMENT_KIND_CHOICES,
    LEVEL_CHOICES,
    LINK_PRIORITY_CHOICES,
    MATERIAL_KIND_CHOICES,
    SECTION_CHOICES,
)
from apps.common.models import Source, Tag, TimeStampedModel


class Material(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    section = models.CharField(max_length=32, choices=SECTION_CHOICES)
    material_kind = models.CharField(max_length=32, choices=MATERIAL_KIND_CHOICES, default="lesson")
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="materials")
    external_url = models.URLField(blank=True)
    primary_file = models.FileField(upload_to="materials/files/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="materials/covers/", blank=True, null=True)
    badge_text = models.CharField(max_length=64, blank=True)
    level = models.CharField(max_length=32, choices=LEVEL_CHOICES, default="general")
    is_external_resource = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(blank=True, null=True)
    link_priority = models.CharField(max_length=16, choices=LINK_PRIORITY_CHOICES, default="external")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_materials",
    )
    tags = models.ManyToManyField(Tag, related_name="materials", blank=True)

    class Meta:
        ordering = ["sort_order", "-published_at", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def target_url(self):
        if self.link_priority == "file" and self.primary_file:
            return self.primary_file.url
        return self.external_url or (self.primary_file.url if self.primary_file else "")

    def __str__(self):
        return self.title


class MaterialAttachment(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="attachments")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="materials/attachments/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    attachment_kind = models.CharField(max_length=32, choices=ATTACHMENT_KIND_CHOICES, default="other")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title

# Create your models here.
