from django.db import models
from django.utils.text import slugify

from apps.catalog.models import Material
from apps.common.choices import DIFFICULTY_CHOICES, EXAM_TYPE_CHOICES, TASK_TYPE_CHOICES
from apps.common.models import Source, Tag, TimeStampedModel


class TestItem(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.TextField(blank=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="tests")
    external_url = models.URLField(blank=True)
    primary_file = models.FileField(upload_to="tests/files/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="tests/covers/", blank=True, null=True)
    exam_type = models.CharField(max_length=32, choices=EXAM_TYPE_CHOICES, default="school_trainer")
    task_type = models.CharField(max_length=32, choices=TASK_TYPE_CHOICES, default="mixed")
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES, default="medium")
    duration_minutes = models.PositiveIntegerField(default=30)
    badge_text = models.CharField(max_length=64, blank=True)
    is_external_resource = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name="tests", blank=True)
    related_materials = models.ManyToManyField(Material, related_name="related_tests", blank=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def target_url(self):
        return self.external_url or (self.primary_file.url if self.primary_file else "")

    def __str__(self):
        return self.title

# Create your models here.
