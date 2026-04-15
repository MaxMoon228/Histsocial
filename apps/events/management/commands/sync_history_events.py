from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Deprecated wrapper for sync_history_calendar"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=3)
        parser.add_argument("--all-pages", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--with-details", action="store_true")
        parser.add_argument("--from-page", type=int, default=1)
        parser.add_argument("--verbose", action="store_true")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Command sync_history_events is deprecated, use sync_history_calendar"))
        call_command(
            "sync_history_calendar",
            pages=options["pages"],
            all_pages=options["all_pages"],
            dry_run=options["dry_run"],
            force=options["force"],
            with_details=options["with_details"],
            from_page=options["from_page"],
            verbose=options["verbose"],
        )
