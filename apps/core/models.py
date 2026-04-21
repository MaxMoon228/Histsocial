from django.db import models


class HomePageAuthorBlock(models.Model):
    section_label = models.CharField(max_length=80, default="Автор проекта")
    photo = models.ImageField(upload_to="core/author/", blank=True, null=True)
    title_text = models.CharField(max_length=255, default="Автор сайта — Билалова Дина Султановна.")
    subtitle_text = models.CharField(
        max_length=400,
        default="Учитель истории и обществознания высшей квалификационной категории, преподаватель СОШИ Лицей имени Н. И. Лобачевского КФУ.",
    )
    description_text = models.TextField(
        default="Проект объединяет академическую точность, современные учебные маршруты и удобную навигацию по ключевым темам."
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Блок автора на главной"
        verbose_name_plural = "Блок автора на главной"

    def __str__(self):
        return f"Автор проекта ({'активен' if self.is_active else 'неактивен'})"
