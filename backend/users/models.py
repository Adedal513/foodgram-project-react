from django.db import models
from django.contrib.auth.models import AbstractUser

USER_REQUIRED_FIELDS = [
    'username',
    'first_name',
    'last_name',
]


class User(AbstractUser):
    email = models.EmailField(
        'email',
        max_length=256,
        unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing_to',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id'],
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscribe_user_author_key'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
