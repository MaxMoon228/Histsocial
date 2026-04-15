from django.core.management.base import BaseCommand

from apps.events.models import HistoricalEvent
from apps.events.services.normalizers import normalize_russian_date


class Command(BaseCommand):
    help = "Rebuild normalized event date fields from display_date_text/title"

    def handle(self, *args, **options):
        updated = 0
        for event in HistoricalEvent.objects.all():
            normalized = normalize_russian_date(event.display_date_text or event.title)
            if normalized["day"] is None and normalized["month"] is None and normalized["year"] is None:
                continue
            event.day = normalized["day"]
            event.month = normalized["month"]
            event.year = normalized["year"]
            event.event_date_precision = normalized["event_date_precision"]
            if not event.display_date_text:
                event.display_date_text = normalized["display_date_text"]
            event.save(update_fields=["day", "month", "year", "event_date_precision", "display_date_text", "updated_at"])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Done. dates_rebuilt={updated}"))
