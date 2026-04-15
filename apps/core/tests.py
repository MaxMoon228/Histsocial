from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class CorePagesTests(TestCase):
    def test_public_pages_status(self):
        for url_name in ["home", "world", "russia", "social", "tests", "calendar", "about", "axis", "favorites", "search"]:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)

    def test_admin_login(self):
        user = get_user_model().objects.create_superuser("admin", "admin@test.com", "admin12345")
        self.assertTrue(self.client.login(username=user.username, password="admin12345"))

    def test_search_page(self):
        response = self.client.get(reverse("search"), {"q": "test"})
        self.assertEqual(response.status_code, 200)
