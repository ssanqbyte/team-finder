

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from core.constants import (
    USER_EMAIL_MAX_LENGTH,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_LAST_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_GITHUB_URL_MAX_LENGTH,
)
from .managers import UserManager  
from .utils import generate_avatar


class User(AbstractBaseUser, PermissionsMixin):
    """Пользователь платформы TeamFinder."""
    
    # Поля модели
    email = models.EmailField(
        "Электронная почта",
        max_length=USER_EMAIL_MAX_LENGTH,  
        unique=True
    )
    first_name = models.CharField(
        "Имя",
        max_length=USER_FIRST_NAME_MAX_LENGTH  
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=USER_LAST_NAME_MAX_LENGTH  
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        null=True
    )
    phone = models.CharField(
        "Телефон",
        max_length=USER_PHONE_MAX_LENGTH,  
        blank=True,
        unique=True,
        null=True
    )
    github_url = models.URLField(
        "Ссылка на GitHub",
        max_length=USER_GITHUB_URL_MAX_LENGTH,  
        blank=True
    )
    
    # Поля для авторизации и прав
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Персонал", default=False)
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)
    last_login = models.DateTimeField("Последний вход", null=True, blank=True)
    
    # Связи
    favorites = models.ManyToManyField(
        "projects.Project",
        verbose_name="Избранное",
        blank=True,
        related_name="favorited_by"
    )
    
    # Настройки аутентификации
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    
    # Менеджер
    objects = UserManager()  
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """Генерация аватарки при создании, если не загружена."""
        if not self.pk and not self.avatar:
            self.avatar = generate_avatar(self.first_name or "U")
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Возвращает краткое имя пользователя."""
        return self.first_name