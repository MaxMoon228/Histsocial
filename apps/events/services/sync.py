import hashlib
import logging
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.common.models import Source, Tag
from apps.events.models import HistoricalEvent
from apps.events.services.importers.base import ImportedEventPayload

logger = logging.getLogger("apps.events.importer")


@dataclass
class SyncStats:
    pages_scanned: int = 0
    cards_found: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0


class HistoryCalendarSyncService:
    SOURCE_SLUG = "historyrussia-org"

    def __init__(self, importer):
        self.importer = importer

    def sync(self, pages=3, all_pages=False, dry_run=False, force=False, with_details=False, from_page=1):
        source = self._get_source(dry_run=dry_run)
        stats = SyncStats()
        payloads = self.importer.fetch_events(pages=pages, from_page=from_page, all_pages=all_pages, with_details=with_details)
        stats.cards_found = len(payloads)
        stats.pages_scanned = pages if not all_pages else max(from_page, from_page + len(payloads))
        now = timezone.now()

        for payload in payloads:
            try:
                if dry_run:
                    logger.info("DRY RUN: %s", payload.title)
                    continue
                outcome = self._upsert_event(source=source, payload=payload, now=now, force=force)
                if outcome == "created":
                    stats.created += 1
                elif outcome == "updated":
                    stats.updated += 1
                else:
                    stats.skipped += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to sync payload '%s': %s", payload.title, exc)
                stats.errors += 1
        return stats

    def _get_source(self, dry_run=False):
        source = Source.objects.filter(slug=self.SOURCE_SLUG).first()
        if not source and dry_run:
            return Source(
                name="Российское историческое общество",
                slug=self.SOURCE_SLUG,
                domain="historyrussia.org",
                base_url=self.importer.source_base_url,
                source_type="external_calendar",
                is_active=True,
            )
        if not source:
            source, _ = Source.objects.get_or_create(
                slug=self.SOURCE_SLUG,
                defaults={
                    "name": "Российское историческое общество",
                    "domain": "historyrussia.org",
                    "base_url": self.importer.source_base_url,
                    "source_type": "external_calendar",
                    "is_active": True,
                },
            )
        if source.base_url != self.importer.source_base_url and not dry_run:
            source.base_url = self.importer.source_base_url
            source.domain = "historyrussia.org"
            source.save(update_fields=["base_url", "domain", "updated_at"])
        return source

    def _get_source_legacy(self):
        # Backward-compat shim for any direct external calls.
        source, _ = Source.objects.get_or_create(
            slug=self.SOURCE_SLUG,
            defaults={
                "name": "Российское историческое общество",
                "domain": "historyrussia.org",
                "base_url": self.importer.source_base_url,
                "source_type": "external_calendar",
                "is_active": True,
            },
        )
        return source

    def _upsert_event(self, source: Source, payload: ImportedEventPayload, now, force=False):
        event = self._find_existing(source, payload)
        defaults = self._payload_to_defaults(payload, now)

        if event and not force and event.source_hash and event.source_hash == defaults["source_hash"]:
            event.last_synced_at = now
            event.import_status = "skipped"
            event.save(update_fields=["last_synced_at", "import_status", "updated_at"])
            return "skipped"

        with transaction.atomic():
            if event is None:
                event = HistoricalEvent(source=source, slug=self._build_unique_slug(payload.title))
                status = "created"
                event.first_seen_at = now
            else:
                status = "updated"
            for key, value in defaults.items():
                setattr(event, key, value)
            if not event.slug:
                event.slug = self._build_unique_slug(payload.title, exclude_id=event.pk)
            event.imported_from_historyrussia = True
            event.last_synced_at = now
            event.import_status = "updated" if status == "updated" else "synced"
            event.save()
            self._apply_tags(event, payload)
        return status

    def _find_existing(self, source: Source, payload: ImportedEventPayload):
        if payload.canonical_url:
            found = HistoricalEvent.objects.filter(source=source, canonical_url=payload.canonical_url).first()
            if found:
                return found
        if payload.source_url:
            found = HistoricalEvent.objects.filter(source=source, source_url=payload.source_url).first()
            if found:
                return found
        if payload.source_uid:
            found = HistoricalEvent.objects.filter(source=source, source_uid=payload.source_uid).first()
            if found:
                return found
        if payload.source_hash:
            return HistoricalEvent.objects.filter(source=source, source_hash=payload.source_hash).first()
        return None

    def _payload_to_defaults(self, payload: ImportedEventPayload, now):
        return {
            "title": payload.title[:255],
            "summary": payload.summary,
            "full_text": payload.full_text,
            "source_url": payload.source_url,
            "canonical_url": payload.canonical_url or payload.source_url,
            "source_domain": "historyrussia.org",
            "image_url_original": payload.image_url,
            "day": payload.day,
            "month": payload.month,
            "year": payload.year,
            "display_date_text": payload.display_date_text,
            "event_date_precision": payload.event_date_precision or "unknown",
            "event_type": payload.event_type or "other",
            "scope": payload.scope or "both",
            "source_hash": payload.source_hash,
            "source_uid": payload.source_uid or self._fallback_uid(payload),
            "raw_payload_json": payload.raw_payload_json or {},
            "raw_html_fragment": payload.raw_html_fragment or "",
            "published_date_at_source": payload.published_date_at_source,
            "is_published": True,
            "imported_from_historyrussia": True,
            "last_synced_at": now,
        }

    def _build_unique_slug(self, title: str, exclude_id=None):
        base_slug = slugify((title or "event")[:210]) or "event"
        slug = base_slug
        idx = 1
        queryset = HistoricalEvent.objects.all()
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        while queryset.filter(slug=slug).exists():
            idx += 1
            slug = f"{base_slug[:220]}-{idx}"
        return slug[:255]

    def _fallback_uid(self, payload: ImportedEventPayload):
        base = payload.canonical_url or payload.source_url or f"{payload.title}-{payload.display_date_text}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:40]

    def _apply_tags(self, event: HistoricalEvent, payload: ImportedEventPayload):
        if not payload.keywords:
            return
        mapped = []
        vocabulary = {
            "война": "Войны",
            "реформа": "Реформы",
            "культура": "Культура",
            "рождение": "Рождение",
            "смерть": "Смерть",
            "договор": "Договоры",
            "россия": "Россия",
            "ссср": "СССР",
        }
        for keyword in payload.keywords:
            for probe, tag_name in vocabulary.items():
                if probe in keyword:
                    mapped.append(tag_name)
        if not mapped:
            return
        tag_ids = []
        for tag_name in sorted(set(mapped)):
            tag, _ = Tag.objects.get_or_create(name=tag_name, defaults={"slug": slugify(tag_name), "tag_type": "event_type"})
            tag_ids.append(tag.id)
        if tag_ids:
            event.tags.add(*tag_ids)
