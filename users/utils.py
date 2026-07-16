"""Утилиты приложения users: генерация первоначальной аватарки."""
import random
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 240
FONT_PATH = (
    settings.BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)

# Приглушённые цвета фона, на которых хорошо читается белая буква.
AVATAR_COLORS = (
    (96, 125, 139),   # серо-синий
    (121, 85, 172),   # фиолетовый
    (67, 118, 108),   # тёмно-бирюзовый
    (192, 108, 67),   # терракотовый
    (85, 110, 190),   # индиго
    (163, 90, 120),   # тёмно-розовый
    (105, 130, 70),   # оливковый
    (70, 130, 160),   # морской
)


def generate_avatar(letter: str) -> ContentFile:
    """Создаёт PNG-аватарку с первой буквой имени на однотонном фоне."""
    letter = (letter or "?").strip()[:1].upper() or "?"
    background = random.choice(AVATAR_COLORS)

    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), background)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(str(FONT_PATH), size=int(AVATAR_SIZE * 0.55))
    except OSError:
        font = ImageFont.load_default(size=int(AVATAR_SIZE * 0.55))

    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    text_width = right - left
    text_height = bottom - top
    position = (
        (AVATAR_SIZE - text_width) / 2 - left,
        (AVATAR_SIZE - text_height) / 2 - top,
    )
    draw.text(position, letter, font=font, fill=(255, 255, 255))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())
