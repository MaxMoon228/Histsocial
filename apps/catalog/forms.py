from django import forms
from django.utils.text import slugify

from apps.common.models import Tag

from .models import Material, MaterialAttachment


class MaterialStaffForm(forms.ModelForm):
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
        model = Material
        fields = [
            "title",
            "slug",
            "short_description",
            "full_description",
            "section",
            "material_kind",
            "source",
            "external_url",
            "primary_file",
            "cover_image",
            "badge_text",
            "level",
            "is_external_resource",
            "is_published",
            "is_archived",
            "sort_order",
            "link_priority",
            "tags",
        ]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "full_description": forms.Textarea(attrs={"rows": 5}),
            "source": forms.Select(attrs={"class": "staff-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean(self):
        cleaned = super().clean()
        external_url = cleaned.get("external_url")
        primary_file = cleaned.get("primary_file")
        if external_url and primary_file:
            raise forms.ValidationError("Для карточки укажите только один источник: либо ссылку, либо файл.")
        if not external_url and not primary_file:
            raise forms.ValidationError("Для карточки укажите источник: ссылку или файл.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)
        if instance.primary_file:
            instance.external_url = ""
            instance.link_priority = "file"
            instance.is_external_resource = False
        else:
            instance.link_priority = "external"
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


class MaterialAttachmentInlineForm(forms.ModelForm):
    delete_flag = forms.BooleanField(required=False)

    class Meta:
        model = MaterialAttachment
        fields = ["title", "file", "external_url", "attachment_kind", "sort_order", "delete_flag"]


class MaterialQuickActionForm(forms.Form):
    ids = forms.CharField()
    action = forms.ChoiceField(choices=[("publish", "Опубликовать"), ("unpublish", "Скрыть"), ("archive", "Архив"), ("delete", "Удалить")])
