import hashlib
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ImportedEventPayload:
    title: str
    summary: str = ""
    full_text: str = ""
    source_url: str = ""
    canonical_url: str = ""
    image_url: str = ""
    display_date_text: str = ""
    day: int | None = None
    month: int | None = None
    year: int | None = None
    event_date_precision: str = "unknown"
    event_type: str = "other"
    scope: str = "both"
    source_uid: str = ""
    keywords: list[str] | None = None
    raw_html_fragment: str = ""
    raw_payload_json: dict[str, Any] | None = None
    published_date_at_source: str | None = None

    @property
    def source_hash(self):
        base = (
            f"{self.canonical_url or self.source_url}|{self.title}|{self.day or ''}|"
            f"{self.month or ''}|{self.year or ''}|{self.display_date_text}"
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()


class BaseCalendarImporter:
    source_name = ""
    source_base_url = ""

    def fetch_events(self, pages=1, from_page=1, all_pages=False, with_details=False):
        raise NotImplementedError
