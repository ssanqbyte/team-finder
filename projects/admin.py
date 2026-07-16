from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Администрирование проектов: редактирование и удаление любых проектов."""

    list_display = ("id", "name", "owner", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "description", "owner__email", "owner__surname")
    filter_horizontal = ("participants",)
    date_hierarchy = "created_at"
