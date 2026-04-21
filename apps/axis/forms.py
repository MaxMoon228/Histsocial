from django import forms
from django.utils.text import slugify

from apps.common.models import Tag

from .models import TimelineNode


class TimelineNodeStaffForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    new_tags = forms.CharField(required=False, help_text="Через запятую")

    class Meta:
        model = TimelineNode
        fields = [
            "title",
            "slug",
            "subtitle",
            "description",
            "scope",
            "scale",
            "start_year",
            "end_year",
            "display_year_text",
            "accent_color",
            "position_order",
            "is_featured",
            "is_published",
            "linked_event",
            "linked_material",
            "linked_test",
            "tags",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "accent_color": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean(self):
        cleaned = super().clean()
        start_year = cleaned.get("start_year")
        end_year = cleaned.get("end_year")
        if end_year is not None and start_year is not None and end_year < start_year:
            raise forms.ValidationError("Конечный год не может быть меньше начального.")
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
                        defaults={"slug": slugify(tag_name), "tag_type": "topic"},
                    )
                    instance.tags.add(tag)
        return instance
