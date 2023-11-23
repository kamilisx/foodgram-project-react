from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
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
