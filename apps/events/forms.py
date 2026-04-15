from django import forms
from django.utils.text import slugify

from apps.common.models import Tag

from .models import HistoricalEvent


class HistoricalEventStaffForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    new_tags = forms.CharField(required=False, help_text="Через запятую")

    class Meta:
        model = HistoricalEvent
        fields = [
            "title",
            "slug",
            "source",
            "source_url",
            "canonical_url",
            "source_domain",
            "summary",
            "full_text",
            "image",
            "image_url_original",
            "day",
            "month",
            "year",
            "display_date_text",
            "event_date_precision",
            "event_type",
            "scope",
            "related_topic_text",
            "is_featured",
            "is_published",
            "imported_from_historyrussia",
            "import_status",
            "published_date_at_source",
            "tags",
            "related_materials",
            "related_tests",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "full_text": forms.Textarea(attrs={"rows": 6}),
            "display_date_text": forms.TextInput(attrs={"placeholder": "14 апреля 1564 года"}),
            "published_date_at_source": forms.DateInput(attrs={"type": "date"}),
            "related_materials": forms.SelectMultiple(),
            "related_tests": forms.SelectMultiple(),
        }

    def clean(self):
        cleaned = super().clean()
        day = cleaned.get("day")
        month = cleaned.get("month")
        if (day and not month) or (month and not day):
            raise forms.ValidationError("Для даты укажите и день, и месяц, либо оставьте оба поля пустыми.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)[:240]
        if commit:
            instance.save()
            self.save_m2m()
            new_tags_raw = self.cleaned_data.get("new_tags", "")
            if new_tags_raw:
                tags = [item.strip() for item in new_tags_raw.split(",") if item.strip()]
                for tag_name in tags:
                    tag, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={"slug": slugify(tag_name), "tag_type": "event_type"},
                    )
                    instance.tags.add(tag)
        return instance
