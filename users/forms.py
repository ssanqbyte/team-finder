from django import forms

from .models import User
from .validators import normalize_phone, validate_github_url, validate_phone_format


class RegisterForm(forms.ModelForm):
    """Форма регистрации нового пользователя."""

    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Электронная почта",
        }

    def save(self, commit=True):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
        )


class LoginForm(forms.Form):
    """Форма входа по email и паролю."""

    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""

    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "avatar": forms.FileInput(attrs={"style": "display: none;"}),
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При редактировании можно не загружать новый аватар —
        # останется текущий.
        self.fields["avatar"].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        validate_phone_format(phone)
        phone = normalize_phone(phone)
        duplicates = User.objects.exclude(pk=self.instance.pk).filter(phone=phone)
        if duplicates.exists():
            raise forms.ValidationError(
                "Пользователь с таким номером телефона уже зарегистрирован."
            )
        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()
        if github_url:
            validate_github_url(github_url)
        return github_url
