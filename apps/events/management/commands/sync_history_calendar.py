from django.conf import settings
from django.core.management.base import BaseCommand

from apps.events.services.importers.historyrussia_html import HistoryRussiaHTMLImporter
from apps.events.services.sync import HistoryCalendarSyncService


class Command(BaseCommand):
    help = "Sync calendar events from historyrussia.org into HistoricalEvent"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=settings.HISTORY_CALENDAR_DEFAULT_PAGES)
        parser.add_argument("--all-pages", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--with-details", action="store_true", default=settings.HISTORY_CALENDAR_WITH_DETAILS)
        parser.add_argument("--from-page", type=int, default=settings.HISTORY_CALENDAR_FROM_PAGE)
        parser.add_argument("--verbose", action="store_true")

    def handle(self, *args, **options):
        importer = HistoryRussiaHTMLImporter(
            base_url=settings.HISTORY_CALENDAR_BASE_URL,
            timeout=settings.HISTORY_CALENDAR_TIMEOUT,
            retries=settings.HISTORY_CALENDAR_RETRIES,
            sleep_s=settings.HISTORY_CALENDAR_SLEEP,
        )
        service = HistoryCalendarSyncService(importer=importer)

        self.stdout.write(self.style.NOTICE("Starting calendar sync..."))
        stats = service.sync(
            pages=options["pages"],
            all_pages=options["all_pages"],
            dry_run=options["dry_run"],
            force=options["force"],
            with_details=options["with_details"],
            from_page=options["from_page"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Calendar sync done: "
                f"pages={stats.pages_scanned}, cards={stats.cards_found}, created={stats.created}, "
                f"updated={stats.updated}, skipped={stats.skipped}, errors={stats.errors}"
            )
        )
