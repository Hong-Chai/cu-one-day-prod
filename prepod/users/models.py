from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    credits = models.IntegerField(default=0, verbose_name="Кредиты")
    expertise = models.TextField(blank=True, verbose_name="Экспертиза")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
