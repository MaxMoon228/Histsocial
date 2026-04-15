from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase

from apps.common.models import Source
from apps.events.admin import HistoricalEventAdmin
from apps.events.models import HistoricalEvent
from apps.events.services.importers.base import ImportedEventPayload
from apps.events.services.importers.historyrussia_html import HistoryRussiaHTMLImporter
from apps.events.services.normalizers import normalize_russian_date
from apps.events.services.sync import HistoryCalendarSyncService


class ImporterTests(TestCase):
    def setUp(self):
        self.importer = HistoryRussiaHTMLImporter(
            base_url="https://historyrussia.org/sobytiya/den-v-istorii.html",
            timeout=5,
            retries=0,
            sleep_s=0,
        )

    def test_parse_card_from_sample_html(self):
        html = """
        <div class="item-page">
          <a href="/sobytiya/den-v-istorii/test-event.html">5 апреля 1242 года — Ледовое побоище</a>
          <p>Краткое описание</p>
        </div>
        """
        from bs4 import BeautifulSoup

        card = BeautifulSoup(html, "lxml").select_one("div")
        payload = self.importer._parse_card(card)
        self.assertEqual(payload.title, "5 апреля 1242 года — Ледовое побоище")
        self.assertEqual(payload.day, 5)
        self.assertEqual(payload.month, 4)
        self.assertEqual(payload.year, 1242)
        self.assertIn("/sobytiya/den-v-istorii/test-event.html", payload.source_url)

    @patch.object(HistoryRussiaHTMLImporter, "_request")
    def test_fetch_with_detail_parses_canonical(self, mock_request):
        list_html = """
        <html><body>
            <a href="/sobytiya/den-v-istorii/test-event-2.html">29 июля 1696 года событие</a>
        </body></html>
        """
        detail_html = """
        <html>
          <head>
            <link rel="canonical" href="https://historyrussia.org/sobytiya/den-v-istorii/test-event-2.html"/>
            <meta name="description" content="Подробное описание"/>
          </head>
          <body>
            <h1>29 июля 1696 года важное событие</h1>
            <article>Полный текст события</article>
          </body>
        </html>
        """
        mock_request.side_effect = [list_html, detail_html]
        payloads = self.importer.fetch_events(pages=1, with_details=True)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0].canonical_url, "https://historyrussia.org/sobytiya/den-v-istorii/test-event-2.html")
        self.assertIn("Подробное", payloads[0].summary)

    def test_normalize_russian_date(self):
        normalized = normalize_russian_date("14 апреля 1564 года")
        self.assertEqual(normalized["day"], 14)
        self.assertEqual(normalized["month"], 4)
        self.assertEqual(normalized["year"], 1564)


class SyncServiceTests(TestCase):
    def setUp(self):
        self.importer = type("FakeImporter", (), {})()
        self.importer.source_base_url = "https://historyrussia.org/sobytiya/den-v-istorii.html"
        self.payload = ImportedEventPayload(
            title="Тестовое событие",
            summary="Кратко",
            source_url="https://historyrussia.org/sobytiya/den-v-istorii/test-sync.html",
            canonical_url="https://historyrussia.org/sobytiya/den-v-istorii/test-sync.html",
            day=10,
            month=3,
            year=1900,
            display_date_text="10 марта 1900",
            event_date_precision="day_month_year",
            source_uid="test-sync",
            raw_payload_json={"x": 1},
        )
        self.importer.fetch_events = lambda **kwargs: [self.payload]
        self.service = HistoryCalendarSyncService(importer=self.importer)

    def test_sync_creates_event(self):
        stats = self.service.sync(pages=1, dry_run=False, with_details=False)
        self.assertEqual(stats.created, 1)
        self.assertEqual(HistoricalEvent.objects.count(), 1)

    def test_sync_updates_existing_without_duplicates(self):
        self.service.sync(pages=1, dry_run=False, with_details=False)
        self.payload.summary = "Обновленный текст"
        stats = self.service.sync(pages=1, dry_run=False, with_details=False, force=True)
        self.assertEqual(stats.updated, 1)
        self.assertEqual(HistoricalEvent.objects.count(), 1)
        self.assertEqual(HistoricalEvent.objects.first().summary, "Обновленный текст")

    def test_sync_skips_when_hash_same(self):
        self.service.sync(pages=1, dry_run=False, with_details=False)
        stats = self.service.sync(pages=1, dry_run=False, with_details=False)
        self.assertGreaterEqual(stats.skipped, 1)
        self.assertEqual(HistoricalEvent.objects.count(), 1)


class CalendarViewTests(TestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="historyrussia.org",
            slug="historyrussia-org-test",
            domain="historyrussia.org",
            base_url="https://historyrussia.org/sobytiya/den-v-istorii.html",
            source_type="external_calendar",
        )
        HistoricalEvent.objects.create(
            title="Событие для календаря",
            slug="calendar-event",
            source=self.source,
            source_url="https://historyrussia.org/sobytiya/den-v-istorii/calendar-event.html",
            day=12,
            month=4,
            year=1961,
            display_date_text="12 апреля 1961",
            imported_from_historyrussia=True,
            is_published=True,
        )

    def test_calendar_page_status_ok(self):
        response = self.client.get("/calendar/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Событие для календаря")

    def test_calendar_day_endpoint_returns_event(self):
        response = self.client.get("/htmx/calendar/day/?mode=month&month=4&day=12&year=2026")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Событие для календаря")


class EventAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(username="admin_events", email="a@a.com", password="pass12345")
        self.source = Source.objects.create(
            name="historyrussia-admin",
            slug="historyrussia-admin",
            domain="historyrussia.org",
            base_url="https://historyrussia.org/sobytiya/den-v-istorii.html",
            source_type="external_calendar",
        )
        self.event = HistoricalEvent.objects.create(
            title="Admin event",
            slug="admin-event",
            source=self.source,
            source_url="https://historyrussia.org/sobytiya/den-v-istorii/admin-event.html",
            day=1,
            month=1,
            imported_from_historyrussia=True,
            is_published=True,
        )

    def test_admin_change_page_available(self):
        client = Client()
        client.force_login(self.user)
        response = client.get(f"/admin/events/historicalevent/{self.event.id}/change/")
        self.assertEqual(response.status_code, 200)

    def test_admin_model_config_has_actions(self):
        model_admin = HistoricalEventAdmin(HistoricalEvent, AdminSite())
        self.assertIn("publish_selected", model_admin.actions)
