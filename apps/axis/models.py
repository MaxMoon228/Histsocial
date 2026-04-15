from django.db import models
from django.utils.text import slugify

from apps.catalog.models import Material
from apps.common.choices import SCALE_CHOICES, SCOPE_CHOICES
from apps.common.models import Tag, TimeStampedModel
from apps.events.models import HistoricalEvent
from apps.tests_catalog.models import TestItem


class TimelineNode(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=16, choices=SCOPE_CHOICES, default="both")
    scale = models.CharField(max_length=16, choices=SCALE_CHOICES, default="year")
    start_year = models.IntegerField()
    end_year = models.IntegerField(blank=True, null=True)
    display_year_text = models.CharField(max_length=120, blank=True)
    is_featured = models.BooleanField(default=False)
    accent_color = models.CharField(max_length=20, default="#915A3B")
    position_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, related_name="timeline_nodes", blank=True)
    linked_event = models.ForeignKey(
        HistoricalEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="timeline_nodes"
    )
    linked_material = models.ForeignKey(
        Material, on_delete=models.SET_NULL, null=True, blank=True, related_name="timeline_nodes"
    )
    linked_test = models.ForeignKey(TestItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="timeline_nodes")

    class Meta:
        ordering = ["position_order", "start_year", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.display_year_text:
            self.display_year_text = f"{self.start_year}" if not self.end_year else f"{self.start_year}-{self.end_year}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# Create your models here.
