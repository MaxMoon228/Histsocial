import logging
import re
import time
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from apps.events.services.normalizers import extract_keywords, infer_event_type, infer_scope, normalize_russian_date

from .base import BaseCalendarImporter, ImportedEventPayload

logger = logging.getLogger("apps.events.importer")


class HistoryRussiaHTMLImporter(BaseCalendarImporter):
    GENERIC_TITLES = {"день в истории", "события в истории", "календарь исторических событий"}

    source_name = "historyrussia.org"

    def __init__(self, base_url: str, timeout: int = 20, retries: int = 3, sleep_s: float = 0.5):
        self.source_base_url = base_url
        self.timeout = timeout
        self.retries = retries
        self.sleep_s = sleep_s
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "IstObshestvoBot/1.0 (+https://historyrussia.org)",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
            }
        )
        retry = Retry(
            total=retries,
            backoff_factor=0.6,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.page_step = 24

    def fetch_events(self, pages=1, from_page=1, all_pages=False, with_details=False):
        results: list[ImportedEventPayload] = []
        seen_urls: set[str] = set()
        current_page = max(1, from_page)
        max_pages = 250 if all_pages else max(1, pages)
        pages_processed = 0

        logger.info("Calendar import started: from_page=%s max_pages=%s with_details=%s", current_page, max_pages, with_details)
        while pages_processed < max_pages:
            page_url = self._build_page_url(current_page)
            try:
                html = self._request(page_url)
            except requests.RequestException as exc:
                logger.error("Failed to fetch page %s: %s", page_url, exc)
                if all_pages:
                    current_page += 1
                    pages_processed += 1
                    continue
                break

            soup = BeautifulSoup(html, "lxml")
            self._update_page_step_from_soup(soup)
            cards = self._extract_cards(soup)
            logger.info("Page %s parsed, cards=%s", current_page, len(cards))
            if not cards:
                if all_pages:
                    break
                current_page += 1
                pages_processed += 1
                continue

            created_on_page = 0
            for card in cards:
                payload = self._parse_card(card)
                if not payload or not payload.source_url:
                    continue
                uid = payload.canonical_url or payload.source_url
                if uid in seen_urls:
                    continue
                seen_urls.add(uid)
                created_on_page += 1
                if with_details:
                    details = self._parse_detail_page(payload.source_url)
                    if details:
                        payload = self._merge_details(payload, details)
                        time.sleep(self.sleep_s)
                results.append(payload)

            if all_pages and created_on_page == 0:
                break
            current_page += 1
            pages_processed += 1

        logger.info("Calendar import finished: pages=%s payloads=%s", pages_processed, len(results))
        return results

    def _build_page_url(self, page: int) -> str:
        if page <= 1:
            return self.source_base_url
        separator = "&" if "?" in self.source_base_url else "?"
        start_offset = max(0, (page - 1) * max(1, self.page_step))
        return f"{self.source_base_url}{separator}start={start_offset}"

    def _update_page_step_from_soup(self, soup: BeautifulSoup):
        starts = []
        for link in soup.select("a[href*='start=']"):
            href = (link.get("href") or "").strip()
            match = re.search(r"[?&]start=(\d+)", href)
            if match:
                starts.append(int(match.group(1)))
        positive = sorted({value for value in starts if value > 0})
        if positive:
            self.page_step = positive[0]

    def _request(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _extract_cards(self, soup: BeautifulSoup):
        cards = []
        for link in soup.select("a[href*='/sobytiya/den-v-istorii/']"):
            href = (link.get("href") or "").strip()
            if not href:
                continue
            if href.endswith("den-v-istorii.html"):
                continue
            if "/sobytiya/den-v-istorii/" not in href:
                continue
            title = link.get_text(" ", strip=True)
            if len(title) < 8:
                continue
            parent = link.find_parent(["article", "li", "div"])
            cards.append(parent or link)
        return cards

    def _parse_card(self, card) -> ImportedEventPayload | None:
        link = card if getattr(card, "name", "") == "a" else card.select_one("a[href*='/sobytiya/den-v-istorii/']")
        if not link:
            return None
        title = link.get_text(" ", strip=True)
        source_url = urljoin(self.source_base_url, link.get("href", "").strip())
        summary_node = card.select_one("p, .introtext, .preview-text, .news-item-text")
        summary = summary_node.get_text(" ", strip=True) if summary_node else ""
        image_node = card.select_one("img[src]")
        image_url = urljoin(self.source_base_url, image_node.get("src", "")) if image_node else ""
        date_text = self._extract_date_text(card.get_text(" ", strip=True), title, summary)
        normalized = normalize_russian_date(date_text)
        event_type = infer_event_type(title, summary)
        scope = infer_scope(title, summary)
        uid = self._source_uid(source_url)
        return ImportedEventPayload(
            title=title[:255],
            summary=summary,
            full_text=summary,
            source_url=source_url,
            canonical_url=source_url,
            image_url=image_url,
            display_date_text=normalized["display_date_text"],
            day=normalized["day"],
            month=normalized["month"],
            year=normalized["year"],
            event_date_precision=normalized["event_date_precision"],
            event_type=event_type,
            scope=scope,
            source_uid=uid,
            keywords=extract_keywords(title, summary),
            raw_html_fragment=str(card)[:10000],
            raw_payload_json={"source_url": source_url, "title": title, "summary": summary, "display_date_text": normalized["display_date_text"]},
        )

    def _extract_date_text(self, text: str, title: str, summary: str) -> str:
        base = " ".join([title, summary, text])
        match = re.search(r"\b\d{1,2}\s+[а-яё]+\s+\d{3,4}\s*(?:года|г\.)?", base.lower())
        if match:
            return match.group(0)
        match2 = re.search(r"\b\d{1,2}\s+[а-яё]+\b", base.lower())
        return match2.group(0) if match2 else ""

    def _parse_detail_page(self, source_url: str) -> dict | None:
        try:
            html = self._request(source_url)
        except requests.RequestException as exc:
            logger.warning("Failed to fetch detail page %s: %s", source_url, exc)
            return None
        soup = BeautifulSoup(html, "lxml")
        title_node = soup.select_one("h1, .item-page h2, .article-title")
        full_text_node = soup.select_one(".item-page, .articleBody, .itemFullText, .entry-content, article")
        summary_node = soup.select_one("meta[name='description']")
        canonical_node = soup.select_one("link[rel='canonical']")
        image_node = soup.select_one("meta[property='og:image'], img[src]")
        date_node = soup.select_one(".item-date, .published, time, .date")

        title = title_node.get_text(" ", strip=True) if title_node else ""
        full_text = full_text_node.get_text(" ", strip=True) if full_text_node else ""
        summary = summary_node.get("content", "").strip() if summary_node else ""
        canonical = canonical_node.get("href", "").strip() if canonical_node else source_url
        image_url = ""
        if image_node:
            image_url = image_node.get("content", "").strip() or image_node.get("src", "").strip()
            if image_url:
                image_url = urljoin(source_url, image_url)
        date_text = date_node.get_text(" ", strip=True) if date_node else self._extract_date_text(full_text[:300], title, summary)
        normalized = normalize_russian_date(date_text)
        return {
            "title": title,
            "summary": summary,
            "full_text": full_text,
            "canonical_url": canonical,
            "image_url": image_url,
            "display_date_text": normalized["display_date_text"],
            "day": normalized["day"],
            "month": normalized["month"],
            "year": normalized["year"],
            "event_date_precision": normalized["event_date_precision"],
            "keywords": extract_keywords(title, summary),
            "raw_payload_json": {
                "canonical_url": canonical,
                "detail_date": date_text,
            },
        }

    def _merge_details(self, payload: ImportedEventPayload, details: dict) -> ImportedEventPayload:
        detail_title = (details.get("title") or "").strip()
        if detail_title and detail_title.lower() not in self.GENERIC_TITLES:
            payload.title = detail_title[:255]
        if details.get("summary"):
            payload.summary = details["summary"]
        if details.get("full_text"):
            payload.full_text = details["full_text"]
        if details.get("canonical_url"):
            payload.canonical_url = details["canonical_url"]
            payload.source_uid = self._source_uid(details["canonical_url"])
        if details.get("image_url"):
            payload.image_url = details["image_url"]
        detail_precision = details.get("event_date_precision") or "unknown"
        payload_precision = payload.event_date_precision or "unknown"
        precision_rank = {"unknown": 0, "day_month": 1, "day_month_year": 2}
        if precision_rank.get(detail_precision, 0) >= precision_rank.get(payload_precision, 0):
            if details.get("display_date_text"):
                payload.display_date_text = details["display_date_text"]
            if details.get("day"):
                payload.day = details["day"]
            if details.get("month"):
                payload.month = details["month"]
            if details.get("year"):
                payload.year = details["year"]
            if details.get("event_date_precision"):
                payload.event_date_precision = details["event_date_precision"]
        if details.get("keywords"):
            payload.keywords = details["keywords"]
        payload.raw_payload_json = {**(payload.raw_payload_json or {}), **details.get("raw_payload_json", {})}
        return payload

    def _source_uid(self, url: str) -> str:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        page_number = query.get("PAGEN_1", [""])[0] or query.get("start", [""])[0]
        return f"{parsed.path}|{page_number}".strip("|")
