from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

# Create your models here.


class ProfileUser(AbstractUser):
    email = models.EmailField(
        "Электронная почта",
        blank=False, null=False,
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        'Имя пользователя',
        blank=False, null=False,
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        blank=False, null=False,
        max_length=150
    )
    follow = models.ManyToManyField(
        'self', related_name='followers', symmetrical=False,
        blank=True)

    class Meta:
        ordering = ["email"]
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"
