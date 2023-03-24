from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

# Create your models here.


class ProfileUser(AbstractUser):
    email = models.EmailField(
        "Электронная почта",
        blank=False,
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя пользователя',
        blank=False,
        max_length=150,
    )
    second_name = models.CharField(
        'Фамилия пользователя',
        blank=False,
        max_length=150,
    )
