from django import forms
from django.utils.text import slugify

from apps.common.models import Source, Tag

from .models import TestItem


class TestItemStaffForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "staff-input"}),
    )
    new_tags = forms.CharField(
        required=False,
        help_text="Через запятую",
        widget=forms.TextInput(attrs={"placeholder": "Новые теги через запятую"}),
    )

    class Meta:
        model = TestItem
        fields = [
            "title",
            "slug",
            "short_description",
            "catalog_section",
            "subject",
            "history_subsection",
            "source",
            "external_url",
            "primary_file",
            "cover_image",
            "exam_type",
            "task_type",
            "difficulty",
            "duration_minutes",
            "badge_text",
            "is_external_resource",
            "is_published",
            "sort_order",
            "tags",
            "related_materials",
        ]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 4}),
            "source": forms.Select(attrs={"class": "staff-input"}),
            "related_materials": forms.SelectMultiple(attrs={"class": "staff-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self._is_activities_form = self._resolve_catalog_section() == "activities"
        if self._is_activities_form:
            optional_for_activities = [
                "short_description",
                "catalog_section",
                "subject",
                "history_subsection",
                "source",
                "cover_image",
                "exam_type",
                "task_type",
                "difficulty",
                "duration_minutes",
                "badge_text",
                "is_external_resource",
                "is_published",
                "sort_order",
                "tags",
                "related_materials",
                "new_tags",
            ]
            for field_name in optional_for_activities:
                if field_name in self.fields:
                    self.fields[field_name].required = False

    def _resolve_catalog_section(self):
        if self.is_bound:
            return self.data.get("catalog_section") or getattr(self.instance, "catalog_section", "testing")
        return getattr(self.instance, "catalog_section", "testing")

    def _activities_default_source(self):
        source, _ = Source.objects.get_or_create(
            slug="activities-manual",
            defaults={
                "name": "Карточки мероприятий (вручную)",
                "domain": "internal",
                "base_url": "",
                "source_type": "external_education",
                "is_active": True,
                "sort_order": 60,
            },
        )
        return source

    def clean(self):
        cleaned = super().clean()
        catalog_section = cleaned.get("catalog_section") or getattr(self.instance, "catalog_section", "testing")
        external_url = cleaned.get("external_url")
        primary_file = cleaned.get("primary_file")
        subject = cleaned.get("subject")
        history_subsection = cleaned.get("history_subsection")
        if external_url and primary_file:
            raise forms.ValidationError("Для карточки укажите только один источник: либо ссылку, либо файл.")
        if not external_url and not primary_file:
            raise forms.ValidationError("Для карточки укажите источник: ссылку или файл.")
        if catalog_section == "activities":
            # Activities don't use quiz/test-specific attributes.
            cleaned["source"] = cleaned.get("source") or self._activities_default_source()
            cleaned["subject"] = "social"
            cleaned["history_subsection"] = ""
            cleaned["exam_type"] = "school_trainer"
            cleaned["task_type"] = "mixed"
            cleaned["difficulty"] = "medium"
            if not cleaned.get("duration_minutes"):
                cleaned["duration_minutes"] = 30
            return cleaned
        if subject != "history":
            cleaned["history_subsection"] = ""
        elif subject == "history" and not history_subsection:
            self.add_error("history_subsection", "Для истории выберите подраздел (XVII или XIX век).")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)
        if instance.catalog_section == "activities":
            if not instance.source_id:
                instance.source = self._activities_default_source()
            instance.subject = "social"
            instance.history_subsection = ""
            instance.exam_type = "school_trainer"
            instance.task_type = "mixed"
            instance.difficulty = "medium"
            if not instance.duration_minutes:
                instance.duration_minutes = 30
        elif instance.subject != "history":
            instance.history_subsection = ""
        if instance.primary_file:
            instance.external_url = ""
            instance.is_external_resource = False
        else:
            instance.is_external_resource = True
        if commit:
            instance.save()
            self.save_m2m()
            new_tags_raw = self.cleaned_data.get("new_tags", "")
            if new_tags_raw:
                tags = [part.strip() for part in new_tags_raw.split(",") if part.strip()]
                for tag_name in tags:
                    tag, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={"slug": slugify(tag_name), "tag_type": "topic"},
                    )
                    instance.tags.add(tag)
        return instance
