from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()

MIN_VALUE = 1
NAME_MAX_CHARACTERS = 150
TEXT_MAX_CHARACTERS = 400
IMAGE_MAX_CHARACTERS = 7


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=NAME_MAX_CHARACTERS,
        unique=True
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=IMAGE_MAX_CHARACTERS,
        validators=(
            RegexValidator(
                regex=r"^#[a-fA-F0-9]{6}$",
                message="Код цвета должен быть в 16-м формате",
                code="wrong_hex_code",
            ),
        ),
    )
    slug = models.SlugField(
        verbose_name="URL",
        unique=True
    )

    class Meta:
        verbose_name = "Tэг"
        verbose_name_plural = "Tэги"
        ordering = ("-pk",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "slug"),
                name="name_slug"
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор",
        null=False,
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=NAME_MAX_CHARACTERS,
        db_index=True,
        null=False,
    )
    image = models.ImageField(
        verbose_name="Картинка рецепта",
        upload_to="recipes",
        null=False,
    )
    text = models.TextField(
        verbose_name="Описание",
        null=False,
        max_length=TEXT_MAX_CHARACTERS
    )
    ingredients = models.ManyToManyField(
        to="Ingredient",
        through="RecipeIngredient",
        related_name="recipe",
        verbose_name="Ингридиенты",
    )
    tags = models.ManyToManyField(
        to="Tag",
        verbose_name="Тэги",
        related_name="recipe",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления ",
        null=False,
        validators=(MinValueValidator(MIN_VALUE),),
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=NAME_MAX_CHARACTERS,
        null=False,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Ед. измерения",
        max_length=NAME_MAX_CHARACTERS,
        null=False
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("-pk",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="name_meas_unit"
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredient",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингридиент",
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(MinValueValidator(MIN_VALUE),),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="recipe_ingredient",
            )
        ]


class FavouriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favourite",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favourite",
    )
    date_added: models.DateTimeField = models.DateTimeField(
        verbose_name="дата создания",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ("-date_added",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favourite"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} добавил "
            f"{self.recipe.name}"
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="user_recipe_shop_cart"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} добавил "
            f"{self.recipe.name} "
        )
