from django.test import TestCase

from .models import Source, Tag


class CommonModelsTests(TestCase):
    def test_source_and_tag_creation(self):
        source = Source.objects.create(name="Test Source", slug="test-source")
        tag = Tag.objects.create(name="Test Tag", slug="test-tag")
        self.assertEqual(str(source), "Test Source")
        self.assertEqual(str(tag), "Test Tag")

# Create your tests here.
