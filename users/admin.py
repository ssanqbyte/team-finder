# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin  
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Административное пользователей: создание, блокировка, смена пароля, удаление."""
    
    list_display = ("id", "email", "first_name", "last_name", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-id",)
    
    
    filter_horizontal = ("groups", "user_permissions", "favorites")
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {
            "fields": ("first_name", "last_name", "avatar", "phone", "github_url")
        }),
        ("Избранное", {"fields": ("favorites",)}),  
        ("Права доступа", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )