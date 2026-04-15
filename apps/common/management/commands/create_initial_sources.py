from django.core.management.base import BaseCommand

from apps.common.models import Source


class Command(BaseCommand):
    help = "Create initial external sources"

    def handle(self, *args, **options):
        items = [
            ("РЭШ", "resh", "resh.edu.ru", "https://resh.edu.ru/", "external_education"),
            ("СДАМГИА ЕГЭ", "sdamgia-ege", "hist-ege.sdamgia.ru", "https://hist-ege.sdamgia.ru/", "external_testing"),
            ("СДАМГИА ОГЭ", "sdamgia-oge", "hist-oge.sdamgia.ru", "https://hist-oge.sdamgia.ru/", "external_testing"),
            ("Президентская библиотека", "prlib", "prlib.ru", "https://www.prlib.ru/", "external_library"),
            ("Runivers", "runivers", "runivers.ru", "https://runivers.ru/", "external_library"),
            (
                "historyrussia.org",
                "historyrussia-org",
                "historyrussia.org",
                "https://historyrussia.org/sobytiya/den-v-istorii.html",
                "external_calendar",
            ),
        ]
        for idx, (name, slug, domain, base_url, source_type) in enumerate(items, start=1):
            Source.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "domain": domain,
                    "base_url": base_url,
                    "source_type": source_type,
                    "sort_order": idx,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Sources initialized"))
