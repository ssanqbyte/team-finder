
from django.conf import settings
from django.db import models
from django.urls import reverse

from core.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_MAX_LENGTH,
)


class Project(models.Model):
    """Pet-проект, для которого автор ищет команду."""
    
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    
    STATUS_CHOICES = [
        (STATUS_OPEN, "Открыт"),
        (STATUS_CLOSED, "Закрыт"),
    ]
    
    name = models.CharField(
        "Название",
        max_length=PROJECT_NAME_MAX_LENGTH
    )
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
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
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
    
    def get_absolute_url(self):
        """Канонический URL для объекта."""
        return reverse('projects:project_detail', kwargs={'project_id': self.id})