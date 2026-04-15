from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Material
from apps.common.models import Source


class FavoritesTests(TestCase):
    def setUp(self):
        source = Source.objects.create(name="S", slug="s")
        self.material = Material.objects.create(
            title="Mat",
            slug="mat",
            section="world",
            material_kind="lesson",
            source=source,
            external_url="https://example.com",
        )

    def test_toggle_favorite(self):
        response = self.client.post(reverse("favorites_toggle"), {"item_type": "materials", "item_id": self.material.id})
        self.assertEqual(response.status_code, 200)
        response2 = self.client.get(reverse("favorites"))
        self.assertContains(response2, "Mat")

# Create your tests here.
