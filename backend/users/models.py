from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    email = models.EmailField(
        unique=True,
        max_length=254
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name="Пользователь",
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор рецепта",
        related_name="following",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="user_not_author",
            ),
            models.UniqueConstraint(
                fields=["user", "author"],
                name="user_author"
            ),
        ]
        ordering = ("-pk",)
        verbose_name = "Подписка"

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
