from .base import BaseCalendarImporter


class FutureApiCalendarImporter(BaseCalendarImporter):
    source_name = "future-api"

    def fetch_events(self, pages=1, from_page=1, all_pages=False, with_details=False):
        return []
