import re

from apps.common.choices import EVENT_TYPE_CHOICES, SCOPE_CHOICES

MONTHS_RU = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def normalize_russian_date(raw_text: str) -> dict:
    text = (raw_text or "").strip().lower()
    if not text:
        return {"day": None, "month": None, "year": None, "display_date_text": "", "event_date_precision": "unknown"}

    # "14 апреля 1564 года", "5 апреля 1242", "29 июля 1696 года"
    dm_y_pattern = re.search(
        r"\b(?P<day>\d{1,2})\s+(?P<month>[а-яё]+)\s*(?P<year>\d{3,4})?\s*(?:года|г\.|год)?\b",
        text,
    )
    if dm_y_pattern:
        day = int(dm_y_pattern.group("day"))
        month_name = dm_y_pattern.group("month")
        month = MONTHS_RU.get(month_name)
        year_match = dm_y_pattern.group("year")
        year = int(year_match) if year_match else None
        if month:
            precision = "day_month_year" if year else "day_month"
            parts = [str(day), month_name]
            if year:
                parts.append(str(year))
            return {
                "day": day,
                "month": month,
                "year": year,
                "display_date_text": " ".join(parts),
                "event_date_precision": precision,
            }

    dd_mm_yyyy = re.search(r"\b(?P<day>\d{1,2})[.\-/](?P<month>\d{1,2})(?:[.\-/](?P<year>\d{4}))?\b", text)
    if dd_mm_yyyy:
        day = int(dd_mm_yyyy.group("day"))
        month = int(dd_mm_yyyy.group("month"))
        year = int(dd_mm_yyyy.group("year")) if dd_mm_yyyy.group("year") else None
        if 1 <= day <= 31 and 1 <= month <= 12:
            return {
                "day": day,
                "month": month,
                "year": year,
                "display_date_text": f"{day:02d}.{month:02d}" + (f".{year}" if year else ""),
                "event_date_precision": "day_month_year" if year else "day_month",
            }

    return {
        "day": None,
        "month": None,
        "year": None,
        "display_date_text": raw_text.strip(),
        "event_date_precision": "unknown",
    }


def infer_event_type(title: str, summary: str) -> str:
    hay = f"{title} {summary}".lower()
    heuristics = {
        "war": ["война", "сражен", "битв", "фронт", "парад", "наступлен"],
        "birth": ["родил", "родился", "рождение"],
        "death": ["умер", "кончина", "смерт"],
        "reform": ["реформ", "указ", "регламент", "манифест"],
        "treaty": ["договор", "соглашени", "мирный договор", "подписан мир"],
        "culture": ["театр", "поэт", "писател", "музей", "культура", "картина", "фильм"],
        "discovery": ["открыт", "открытие", "экспедици", "изобрет"],
        "holiday": ["праздник", "день ", "юбилей"],
    }
    for event_type, words in heuristics.items():
        if any(word in hay for word in words):
            return event_type
    valid = {item[0] for item in EVENT_TYPE_CHOICES}
    return "other" if "other" in valid else next(iter(valid))


def infer_scope(title: str, summary: str) -> str:
    hay = f"{title} {summary}".lower()
    world_markers = ["франц", "герман", "британ", "сша", "европ", "миров"]
    russia_markers = ["росси", "рус", "ссср", "петр", "москва", "санкт-петербург"]
    has_world = any(marker in hay for marker in world_markers)
    has_russia = any(marker in hay for marker in russia_markers)
    valid = {item[0] for item in SCOPE_CHOICES}
    if has_world and not has_russia and "world" in valid:
        return "world"
    if has_russia and not has_world and "russia" in valid:
        return "russia"
    return "both" if "both" in valid else next(iter(valid))


def extract_keywords(title: str, summary: str) -> list[str]:
    text = f"{title} {summary}".lower()
    words = re.findall(r"[а-яёa-z0-9-]{4,}", text)
    blacklist = {"года", "истории", "события", "день", "всего", "этого", "также"}
    unique = []
    for word in words:
        if word in blacklist:
            continue
        if word not in unique:
            unique.append(word)
    return unique[:12]
