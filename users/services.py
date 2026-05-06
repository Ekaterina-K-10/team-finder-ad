import colorsys
import hashlib
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from constants import AVATAR_FONT_SIZE, AVATAR_SIZE


def generate_avatar(user):
    """Генерация аватара для пользователя"""
    letter = user.name[0].upper() if user.name else '?'

    hash_obj = hashlib.md5(user.email.encode())
    hash_hex = hash_obj.hexdigest()
    hue = int(hash_hex[:6], 16) % 360
    saturation = 0.5
    lightness = 0.6
    rgb = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
    bg_color = tuple(int(c * 255) for c in rgb)

    size = AVATAR_SIZE
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', AVATAR_FONT_SIZE)
    except (IOError, OSError, FileNotFoundError):
        try:
            font = ImageFont.truetype(
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                AVATAR_FONT_SIZE
            )
        except (IOError, OSError, FileNotFoundError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    draw.text((x, y), letter, fill=(255, 255, 255), font=font)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f'avatar_{user.email}.png')
