import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create admin user from environment variables"

    def handle(self, *args, **options):
        username = os.getenv("SUPERUSER_USERNAME", "admin")
        email = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("SUPERUSER_PASSWORD", "admin12345")
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin user already exists")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Admin user {username} created"))
