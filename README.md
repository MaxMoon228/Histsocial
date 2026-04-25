# Истобщество

Production-ready MVP+ агрегатора исторических материалов на Django, PostgreSQL и Docker.

## Возможности

- Публичные разделы: `/`, `/world/`, `/russia/`, `/tests/`, `/calendar/`, `/about/`, `/axis/`, `/favorites/`, `/search/`
- Полноценная Django Admin: `/admin/` (только staff/superuser)
- Избранное без логина через `django session`
- Глобальный поиск + автоподсказки
- Исторический календарь с импортом `historyrussia.org`
- Историческая ось по `TimelineNode`
- Логирование поисковых запросов и внешних переходов

## Технологии

- Python 3.12, Django 5.x
- PostgreSQL 16
- Gunicorn + Nginx
- HTMX + Alpine.js + Django Templates
- requests + BeautifulSoup4 + lxml

## Локальный запуск (без Docker)

```bash
python -m pip install -r requirements/dev.txt
copy .env.example .env
python manage.py migrate
python manage.py create_initial_sources
python manage.py create_admin_user
python manage.py seed_demo_content
python manage.py runserver
```

## Docker запуск

```bash
copy .env.example .env
docker compose up --build
```

После старта открыть: [http://localhost](http://localhost)

## Deploy на Render через Dockerfile

В репозитории добавлен `render.yaml` (Blueprint):
- Web service (`env: docker`, сборка из корневого `Dockerfile`)
- PostgreSQL (Render DB)
- Cron job для ежедневного импорта календаря

Шаги:
1. Откройте Render Dashboard.
2. **New +** → **Blueprint**.
3. Выберите репозиторий `MaxMoon228/Histsocial`.
4. Подтвердите создание сервисов из `render.yaml`.
5. После первого деплоя откройте web-сервис и проверьте переменные окружения.
6. Убедитесь, что задано:
   - `DJANGO_SETTINGS_MODULE=config.settings.prod`
   - `DATABASE_URL` (связан с Render PostgreSQL)
7. Выполните `Manual Deploy`.
8. Проверьте:
   - `/health/` → `200`
   - `/` → открывается без `500`

Что запускается на web старте:
- `migrate`
- `collectstatic`
- `create_initial_sources`
- `create_admin_user`
- `create_default_staff`
- `seed_demo_content`

Cron-сервис ежедневно выполняет:
`python manage.py sync_history_calendar --pages 3 --with-details`

## Полезные команды

```bash
python manage.py create_admin_user
python manage.py create_initial_sources
python manage.py seed_timeline_nodes
python manage.py seed_demo_content
python manage.py sync_history_calendar --pages 3 --with-details
python manage.py sync_history_calendar --pages 1 --dry-run
python manage.py sync_history_calendar --all-pages --from-page 1 --with-details
python manage.py backfill_event_slugs
python manage.py rebuild_event_dates
```

## Структура окружения `.env`

- `DJANGO_SETTINGS_MODULE` (`config.settings.dev` / `config.settings.prod`)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL` (приоритетный вариант для production/Render)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `SUPERUSER_USERNAME`, `SUPERUSER_EMAIL`, `SUPERUSER_PASSWORD`
- `DEFAULT_STAFF_USERNAME`, `DEFAULT_STAFF_PASSWORD`, `DEFAULT_STAFF_EMAIL`
- `HISTORY_CALENDAR_BASE_URL`
- `HISTORY_CALENDAR_TIMEOUT`
- `HISTORY_CALENDAR_RETRIES`
- `HISTORY_CALENDAR_SLEEP`
- `HISTORY_CALENDAR_DEFAULT_PAGES`
- `HISTORY_CALENDAR_WITH_DETAILS` (`1`/`0`)
- `HISTORY_CALENDAR_FROM_PAGE`
- `HISTORY_CALENDAR_CRON` (cron-расписание запуска в scheduler-контейнере)
- `TZ`

## Парсер календаря

- Основной провайдер: `apps/events/services/importers/historyrussia_html.py`
- Provider pattern:
  - `BaseCalendarImporter`
  - `HistoryRussiaHTMLImporter`
  - `FutureApiCalendarImporter` (placeholder)
- Сервис синхронизации: `apps/events/services/sync.py`
- Нормализация даты и эвристики: `apps/events/services/normalizers.py`
- Основная команда импорта: `sync_history_calendar`
  - `--pages 3`
  - `--all-pages`
  - `--dry-run`
  - `--force`
  - `--with-details`
  - `--from-page 1`
- Импорт идемпотентный (upsert по canonical/source URL и source UID), без дублей.
- Scheduler-контейнер выполняет импорт ежедневно из локального Docker stack и пишет логи в stdout/stderr.
- Публичная страница `/calendar/` читает события только из локальной БД, а не из live-запросов к источнику.

## Модерация импортированных событий

- Откройте `/admin/events/historicalevent/`.
- Доступно редактирование текста, даты, тегов, связей с материалами/тестами, публикации.
- Быстрые admin actions:
  - publish selected
  - unpublish selected
  - re-slug selected
  - mark as featured / mark as not featured

## Тесты

```bash
python manage.py test
```
