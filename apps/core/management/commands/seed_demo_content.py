from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.catalog.models import Material
from apps.common.models import Source, Tag
from apps.events.models import HistoricalEvent
from apps.tests_catalog.models import TestItem


class Command(BaseCommand):
    help = "Seed demo content for all public pages"

    def handle(self, *args, **options):
        call_command("create_initial_sources")
        world_tag, _ = Tag.objects.get_or_create(name="Всеобщая история", slug="world", tag_type="region")
        russia_tag, _ = Tag.objects.get_or_create(name="История России", slug="russia", tag_type="region")
        social_tag, _ = Tag.objects.get_or_create(name="Обществознание", slug="social", tag_type="region")
        event_tag, _ = Tag.objects.get_or_create(name="Календарь", slug="calendar", tag_type="topic")

        resh = Source.objects.get(slug="resh")
        ege = Source.objects.get(slug="sdamgia-ege")
        history = Source.objects.get(slug="historyrussia-org")

        world_materials = [
            ("Всемирная история: учебные уроки", "https://resh.edu.ru/subject/3/"),
            ("Всеобщая история. 5 класс", "https://resh.edu.ru/subject/3/5/"),
            ("Всеобщая история. 6 класс", "https://resh.edu.ru/subject/3/6/"),
            ("Всеобщая история. 8 класс", "https://resh.edu.ru/subject/3/8/"),
            ("Древние цивилизации", "https://resh.edu.ru/subject/lesson/7519/"),
            ("Французская революция", "https://resh.edu.ru/subject/lesson/2080/train/"),
            ("Индустриальная эпоха", "https://runivers.ru/library/vseobshchaya-istoriya/alphabet/name/a/"),
            ("Холодная война", "https://resh.edu.ru/subject/lesson/2529/train/"),
        ]
        for i, (title, url) in enumerate(world_materials, start=1):
            obj, _ = Material.objects.update_or_create(
                slug=f"world-{i}",
                defaults={
                    "title": title,
                    "short_description": "Подборка внешнего учебного материала.",
                    "section": "world",
                    "material_kind": "lesson",
                    "source": resh,
                    "external_url": url,
                    "level": "school_basic",
                    "sort_order": i,
                    "is_published": True,
                },
            )
            obj.tags.set([world_tag])

        russia_materials = [
            ("Древняя Русь", "https://www.prlib.ru/item/416891"),
            ("Московское государство", "https://www.prlib.ru/collections_all"),
            ("Пётр I и реформы", "https://hist-ege.sdamgia.ru/handbook"),
            ("Отечественная война 1812 года", "https://old.runivers.ru/lib/book3041/9590/"),
            ("Российская империя", "https://www.prlib.ru/catalog"),
            ("Революции начала XX века", "https://runivers.ru/lib/rubriks/?PAGEN_1=2&search_by=title"),
            ("СССР в 1920–1930-е", "https://old.runivers.ru/lib/rubriks/"),
            ("Великая Отечественная война", "https://old.runivers.ru/gal/maps.php"),
        ]
        for i, (title, url) in enumerate(russia_materials, start=1):
            obj, _ = Material.objects.update_or_create(
                slug=f"russia-{i}",
                defaults={
                    "title": title,
                    "short_description": "Ключевая тема по истории России.",
                    "section": "russia",
                    "material_kind": "textbook",
                    "source": resh,
                    "external_url": url,
                    "level": "school_basic",
                    "sort_order": i,
                    "is_published": True,
                },
            )
            obj.tags.set([russia_tag])

        social_topics = {
            "Человек и общество": "topic-human-society",
            "Экономика": "topic-economy",
            "Социальные отношения": "topic-social-relations",
            "Политика": "topic-politics",
            "Право": "topic-law",
            "Духовная культура": "topic-culture",
            "ЕГЭ": "topic-ege",
            "ОГЭ": "topic-oge",
        }
        social_topic_tags = {}
        for topic_name, topic_slug in social_topics.items():
            social_topic_tags[topic_name], _ = Tag.objects.get_or_create(name=topic_name, slug=topic_slug, tag_type="topic")

        social_materials = [
            ("Человек и общество", "https://resh.edu.ru/subject/lesson/1512/", ["Человек и общество"]),
            ("Экономика: спрос, предложение, рынок", "https://resh.edu.ru/subject/lesson/1540/", ["Экономика"]),
            ("Социальная структура общества", "https://resh.edu.ru/subject/lesson/1538/", ["Социальные отношения"]),
            ("Политическая система", "https://resh.edu.ru/subject/lesson/1537/", ["Политика"]),
            ("Конституция РФ и основы права", "https://resh.edu.ru/subject/lesson/1542/", ["Право"]),
            ("Формы государства", "https://resh.edu.ru/subject/lesson/1541/", ["Политика", "Право"]),
            ("Духовная культура и наука", "https://resh.edu.ru/subject/lesson/1545/", ["Духовная культура"]),
            ("ЕГЭ: задания по праву", "https://hist-ege.sdamgia.ru/prob_catalog", ["ЕГЭ", "Право"]),
            ("ОГЭ: базовый тренажёр", "https://hist-oge.sdamgia.ru/prob-catalog", ["ОГЭ"]),
            ("Налоги и государственный бюджет", "https://resh.edu.ru/subject/lesson/1544/", ["Экономика"]),
            ("Гражданское общество и правовое государство", "https://resh.edu.ru/subject/lesson/1543/", ["Право", "Человек и общество"]),
            ("Роль семьи и социальных институтов", "https://resh.edu.ru/subject/lesson/1539/", ["Социальные отношения"]),
        ]
        for i, (title, url, tags) in enumerate(social_materials, start=1):
            obj, _ = Material.objects.update_or_create(
                slug=f"social-{i}",
                defaults={
                    "title": title,
                    "short_description": "Материал по обществознанию для подготовки к урокам и экзаменам.",
                    "section": "social",
                    "material_kind": "lesson" if i < 8 else "pdf",
                    "source": resh,
                    "external_url": url,
                    "level": "exam" if i in [8, 9] else "school_basic",
                    "sort_order": 200 + i,
                    "is_published": True,
                },
            )
            obj.tags.set([social_tag, *[social_topic_tags[tag] for tag in tags]])

        test_items = [
            ("Хронология событий", "dates"),
            ("Исторические личности", "persons"),
            ("Работа с источником", "sources"),
            ("Карта и схема", "maps"),
            ("Термины и понятия", "terms"),
            ("Реформы Петра I", "reforms"),
            ("СССР и международные отношения", "wars"),
        ]
        for i, (title, task_type) in enumerate(test_items, start=1):
            obj, _ = TestItem.objects.update_or_create(
                slug=f"test-{i}",
                defaults={
                    "title": title,
                    "short_description": "Практический блок заданий для закрепления темы.",
                    "source": ege,
                    "external_url": "https://hist-ege.sdamgia.ru/prob_catalog",
                    "exam_type": "ege",
                    "task_type": task_type,
                    "difficulty": "medium",
                    "duration_minutes": 30,
                    "sort_order": i,
                    "is_published": True,
                },
            )
            obj.tags.set([russia_tag])

        event_items = [
            ("Основание Санкт-Петербурга", 27, 5, 1703, "spb-1703"),
            ("Начало Отечественной войны 1812 года", 24, 6, 1812, "war1812"),
            ("Полет Гагарина", 12, 4, 1961, "gagarin"),
            ("Крещение Руси", 28, 7, 988, "baptism"),
        ]
        for title, day, month, year, key in event_items:
            obj, _ = HistoricalEvent.objects.update_or_create(
                source=history,
                source_url=f"https://historyrussia.org/sobytiya/{key}.html",
                defaults={
                    "slug": f"event-{key}",
                    "title": title,
                    "summary": "Демо-событие для наполнения календаря.",
                    "day": day,
                    "month": month,
                    "year": year,
                    "display_date_text": f"{day:02d}.{month:02d}.{year}",
                    "scope": "russia",
                    "event_type": "other",
                    "is_published": True,
                    "imported_from_historyrussia": True,
                },
            )
            obj.tags.set([event_tag])

        call_command("seed_timeline_nodes")
        self.stdout.write(self.style.SUCCESS("Demo content seeded"))
