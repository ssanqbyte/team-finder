"""Общие валидаторы форм проекта."""
import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError

PHONE_PATTERN = re.compile(r"^(?:8|\+7)\d{10}$")
GITHUB_HOSTS = ("github.com", "www.github.com")


def normalize_phone(phone: str) -> str:
    """Приводит номер телефона к единому формату +7XXXXXXXXXX."""
    phone = (phone or "").strip()
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


def validate_phone_format(phone: str) -> None:
    """Проверяет формат номера: 8XXXXXXXXXX либо +7XXXXXXXXXX."""
    if not PHONE_PATTERN.match(phone):
        raise ValidationError(
            "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )


def validate_github_url(url: str) -> None:
    """Проверяет, что ссылка ведёт именно на GitHub."""
    host = (urlparse(url).netloc or "").lower()
    if host not in GITHUB_HOSTS:
        raise ValidationError("Ссылка должна вести на github.com.")
