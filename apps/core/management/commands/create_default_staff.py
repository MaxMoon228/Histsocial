import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default staff user for local/editor login"

    def handle(self, *args, **options):
        username = os.getenv("DEFAULT_STAFF_USERNAME", "Истобщество")
        password = os.getenv("DEFAULT_STAFF_PASSWORD", "12345")
        email = os.getenv("DEFAULT_STAFF_EMAIL", "staff@example.com")
        user_model = get_user_model()

        user = user_model.objects.filter(username=username).first()
        if user:
            if not user.is_staff:
                user.is_staff = True
                user.save(update_fields=["is_staff"])
                self.stdout.write(self.style.WARNING(f"User {username} promoted to staff"))
            else:
                self.stdout.write("Default staff already exists")
            return

        user_model.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Default staff {username} created"))
