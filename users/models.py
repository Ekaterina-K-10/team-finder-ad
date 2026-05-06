from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image, ImageDraw, ImageFont
import hashlib
from io import BytesIO
from django.core.files.base import ContentFile
import colorsys


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png'
    )
    phone = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                r'^\+7\d{10}$',
                'Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7)'
            )
        ]
    )
    github_url = models.URLField(
        blank=True,
        validators=[
            RegexValidator(
                r'^https?://github\.com/',
                'Ссылка должна вести на GitHub'
            )
        ]
    )
    about = models.TextField(max_length=256, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.avatar or self.avatar.name == 'avatars/default.png':
            self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        letter = self.name[0].upper() if self.name else "?"

        # Генерация цвета на основе email
        hash_obj = hashlib.md5(self.email.encode())
        hash_hex = hash_obj.hexdigest()
        hue = int(hash_hex[:6], 16) % 360
        saturation = 0.5
        lightness = 0.6
        rgb = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
        bg_color = tuple(int(c * 255) for c in rgb)

        size = 200
        image = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(image)

        # Попытка загрузить шрифт
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
        except (IOError, OSError, FileNotFoundError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 100)
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
        self.avatar.save(
            f'avatar_{self.email}.png',
            ContentFile(buffer.getvalue()),
            save=False
        )

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"

    def __str__(self):
        return self.full_name
