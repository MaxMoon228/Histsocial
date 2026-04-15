from django.db import models


class FavoriteSessionItem(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)
    content_type = models.CharField(max_length=20)
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("session_key", "content_type", "object_id")

    def __str__(self):
        return f"{self.session_key}:{self.content_type}:{self.object_id}"

# Create your models here.
