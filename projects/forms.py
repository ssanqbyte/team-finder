from django import forms

from users.validators import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта."""

    status = forms.ChoiceField(
        label="Статус",
        choices=[("open", "Открыт"), ("closed", "Закрыт")],
    )

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()
        if github_url:
            validate_github_url(github_url)
        return github_url
