from django.conf import settings
from django.db import models


class Project(models.Model):
    """Pet-проект, для которого автор ищет команду."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    status = models.CharField(
        "Статус",
        max_length=6,
        choices=STATUS_CHOICES,
        default="open",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Участники",
        related_name="participated_projects",
        blank=True,
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="project_created_at_idx"),
        ]

    def __str__(self):
        return self.name
