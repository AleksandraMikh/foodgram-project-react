from django.db import models
from django.contrib.auth.models import AbstractUser


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
        'self', related_name='followers',
        blank=True, through='Follow')

    class Meta:
        ordering = ["email"]
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"


class Follow(models.Model):
    user = models.ForeignKey(ProfileUser,
                             related_name='following',
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(ProfileUser,
                               related_name='followers',
                               on_delete=models.CASCADE
                               )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='user_unique_follow'
            )
        ]
        verbose_name_plural = "Подписки"
        verbose_name = "Подписка"
