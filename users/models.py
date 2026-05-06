from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import RegexValidator
from django.db import models

from constants import (USER_ABOUT_MAX_LENGTH, USER_FIRST_NAME_MAX_LENGTH,
                       USER_PHONE_MAX_LENGTH, USER_SURNAME_MAX_LENGTH)


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
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    name = models.CharField(max_length=USER_FIRST_NAME_MAX_LENGTH, verbose_name='Имя')
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH, verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        default='',
        validators=[
            RegexValidator(
                r'^\+7\d{10}$',
                'Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7)'
            )
        ],
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        default='',
        validators=[
            RegexValidator(
                r'^https?://github\.com/',
                'Ссылка должна вести на GitHub'
            )
        ],
        verbose_name='GitHub'
    )
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
        default='',
        verbose_name='О себе'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True,
        verbose_name='Избранные проекты'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def save(self, *args, **kwargs):
        from .services import generate_avatar
        if not self.avatar or self.avatar.name == 'avatars/default.png':
            self.avatar = generate_avatar(self)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.full_name
