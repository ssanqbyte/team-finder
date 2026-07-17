# users/utils.py

"""Утилиты приложения users: генерация первоначальной аватарки."""
import random
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

# ============ Константы для аватарок ============
AVATAR_SIZE = 240
AVATAR_FONT_SIZE_RATIO = 0.55  # Размер шрифта относительно размера аватарки
AVATAR_TEXT_COLOR = (255, 255, 255)  # Белый цвет для текста

# Приглушённые цвета фона, на которых хорошо читается белая буква.
# Определяем отдельные цвета с понятными именами
COLOR_SLATE_BLUE = (96, 125, 139)      # серо-синий
COLOR_PURPLE = (121, 85, 172)           # фиолетовый
COLOR_TEAL = (67, 118, 108)             # тёмно-бирюзовый
COLOR_TERRACOTTA = (192, 108, 67)       # терракотовый
COLOR_INDIGO = (85, 110, 190)           # индиго
COLOR_DARK_PINK = (163, 90, 120)        # тёмно-розовый
COLOR_OLIVE = (105, 130, 70)            # оливковый
COLOR_SEA_BLUE = (70, 130, 160)         # морской

# Список доступных цветов для фона аватарки
AVATAR_COLORS = (
    COLOR_SLATE_BLUE,
    COLOR_PURPLE,
    COLOR_TEAL,
    COLOR_TERRACOTTA,
    COLOR_INDIGO,
    COLOR_DARK_PINK,
    COLOR_OLIVE,
    COLOR_SEA_BLUE,
)

# Путь к шрифту
FONT_PATH = (
    settings.BASE_DIR / "static" / "fonts" /
    "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)


def generate_avatar(letter: str) -> ContentFile:
    """
    Создаёт PNG-аватарку с первой буквой имени на однотонном фоне.
    
    Args:
        letter: Первая буква имени пользователя
        
    Returns:
        ContentFile: Файл аватарки в формате PNG
    """
    letter = (letter or "?").strip()[:1].upper() or "?"
    background = random.choice(AVATAR_COLORS)

    # Создаём изображение
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), background)
    draw = ImageDraw.Draw(image)

    # Загружаем шрифт
    font_size = int(AVATAR_SIZE * AVATAR_FONT_SIZE_RATIO)
    try:
        font = ImageFont.truetype(str(FONT_PATH), size=font_size)
    except OSError:
        # Если шрифт не найден, используем стандартный
        font = ImageFont.load_default(size=font_size)

    # Вычисляем позицию текста по центру
    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    text_width = right - left
    text_height = bottom - top
    position = (
        (AVATAR_SIZE - text_width) / 2 - left,
        (AVATAR_SIZE - text_height) / 2 - top,
    )

    # Рисуем текст
    draw.text(position, letter, font=font, fill=AVATAR_TEXT_COLOR)

    # Сохраняем в BytesIO и возвращаем как ContentFile
    image_io = BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)
    
    return ContentFile(image_io.read(), name=f"avatar_{letter}.png")