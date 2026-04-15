from django.db import models
from django.utils.text import slugify

from apps.catalog.models import Material
from apps.common.choices import EVENT_TYPE_CHOICES, SCOPE_CHOICES
from apps.common.models import Source, Tag, TimeStampedModel
from apps.tests_catalog.models import TestItem


class HistoricalEvent(TimeStampedModel):
    DATE_PRECISION_CHOICES = [
        ("unknown", "Не определено"),
        ("day_month", "День и месяц"),
        ("day_month_year", "День, месяц и год"),
    ]
    IMPORT_STATUS_CHOICES = [
        ("synced", "Синхронизировано"),
        ("updated", "Обновлено"),
        ("skipped", "Пропущено"),
        ("error", "Ошибка"),
        ("manual", "Ручное"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="events")
    source_url = models.URLField(blank=True)
    canonical_url = models.URLField(blank=True)
    source_domain = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    full_text = models.TextField(blank=True)
    image = models.ImageField(upload_to="events/images/", blank=True, null=True)
    image_url_original = models.URLField(blank=True)
    day = models.PositiveSmallIntegerField(blank=True, null=True, db_index=True)
    month = models.PositiveSmallIntegerField(blank=True, null=True, db_index=True)
    year = models.IntegerField(blank=True, null=True, db_index=True)
    display_date_text = models.CharField(max_length=120, blank=True)
    event_date_precision = models.CharField(max_length=20, choices=DATE_PRECISION_CHOICES, default="unknown")
    published_date_at_source = models.DateField(blank=True, null=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES, default="other")
    scope = models.CharField(max_length=16, choices=SCOPE_CHOICES, default="both")
    related_topic_text = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    imported_from_historyrussia = models.BooleanField(default=False)
    import_status = models.CharField(max_length=16, choices=IMPORT_STATUS_CHOICES, default="synced")
    source_hash = models.CharField(max_length=64, blank=True, db_index=True)
    source_uid = models.CharField(max_length=255, blank=True, db_index=True)
    raw_payload_json = models.JSONField(default=dict, blank=True)
    raw_html_fragment = models.TextField(blank=True)
    first_seen_at = models.DateTimeField(blank=True, null=True, db_index=True)
    last_synced_at = models.DateTimeField(blank=True, null=True, db_index=True)
    tags = models.ManyToManyField(Tag, related_name="events", blank=True)
    related_materials = models.ManyToManyField(Material, related_name="events", blank=True)
    related_tests = models.ManyToManyField(TestItem, related_name="events", blank=True)

    class Meta:
        ordering = ["month", "day", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "source_url"],
                name="unique_event_source_url",
                condition=~models.Q(source_url=""),
            ),
            models.UniqueConstraint(
                fields=["source", "canonical_url"],
                name="unique_event_source_canonical_url",
                condition=~models.Q(canonical_url=""),
            ),
            models.UniqueConstraint(
                fields=["source", "source_uid"],
                name="unique_event_source_uid",
                condition=~models.Q(source_uid=""),
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240]
        super().save(*args, **kwargs)

    @property
    def target_url(self):
        return self.source_url

    def __str__(self):
        return self.title

# Create your models here.
