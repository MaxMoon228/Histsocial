from django.core.management.base import BaseCommand

from apps.axis.models import TimelineNode


class Command(BaseCommand):
    help = "Seed default timeline nodes"

    def handle(self, *args, **options):
        nodes = [
            ("Рюрик", 862, "Начало династической истории"),
            ("Крещение Руси", 988, "Принятие христианства"),
            ("Ледовое побоище", 1242, "Победа Александра Невского"),
            ("Куликовская битва", 1380, "Символ объединения русских земель"),
            ("Конец ига", 1480, "Стояние на реке Угре"),
            ("Иван Грозный", 1547, "Первый русский царь"),
            ("Романовы", 1613, "Новая династия"),
            ("Северная война", 1700, "Реформы и усиление России"),
            ("1812 год", 1812, "Отечественная война"),
        ]
        for pos, (title, start_year, subtitle) in enumerate(nodes, start=1):
            TimelineNode.objects.update_or_create(
                slug=title.lower().replace(" ", "-"),
                defaults={
                    "title": title,
                    "subtitle": subtitle,
                    "description": subtitle,
                    "scope": "russia",
                    "scale": "year",
                    "start_year": start_year,
                    "display_year_text": str(start_year),
                    "position_order": pos,
                    "is_published": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Timeline nodes seeded"))
