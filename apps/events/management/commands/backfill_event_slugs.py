from django.core.management.base import BaseCommand

from apps.events.models import HistoricalEvent


class Command(BaseCommand):
    help = "Backfill/repair slugs for historical events"

    def handle(self, *args, **options):
        fixed = 0
        for event in HistoricalEvent.objects.all().order_by("id"):
            if event.slug:
                continue
            event.slug = ""
            event.save(update_fields=["slug", "updated_at"])
            fixed += 1
        self.stdout.write(self.style.SUCCESS(f"Done. slugs_fixed={fixed}"))
