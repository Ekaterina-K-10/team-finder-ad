from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(
        blank=True,
        validators=[
            RegexValidator(
                r'^https?://github\.com/',
                'Ссылка должна вести на GitHub'
            )
        ]
    )
    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES,
        default='open'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True
    )

    def __str__(self):
        return self.name
