from django import forms

from .models import User
from .validators import normalize_phone, validate_github_url, validate_phone_format


class RegisterForm(forms.ModelForm):
    """Форма регистрации нового пользователя."""

    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

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
    class Meta:
        model = User
        fields = ("first_name", "last_name", "avatar", "phone", "github_url")
        widgets = {
            "avatar": forms.FileInput(attrs={"style": "display: none;"}),
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

