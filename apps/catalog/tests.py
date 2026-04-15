from django.test import TestCase

from apps.common.models import Source

from .models import Material


class MaterialModelTests(TestCase):
    def test_material_target_url_external_first(self):
        source = Source.objects.create(name="S", slug="s")
        material = Material.objects.create(
            title="M",
            slug="m",
            section="world",
            material_kind="lesson",
            source=source,
            external_url="https://example.com",
        )
        self.assertEqual(material.target_url, "https://example.com")

# Create your tests here.
