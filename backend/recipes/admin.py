from django.contrib import admin

from .models import (FavouriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "get_favorite_count",
    )
    search_fields = (
        "name",
        "author__username",
        "tags",
    )
    list_filter = (
        "name",
        "author__username",
        "tags",
    )
    list_select_related = ["author", ]

    def get_queryset(self, request):
        qs = super(RecipeAdmin, self).queryset(request)
        return qs.prefetch_related("tags", "ingredients")

    inlines = (RecipeIngredientAdmin,)

    @admin.display(description="Избранное")
    def get_favorite_count(self, obj):
        return obj.favourite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(FavouriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user__username", "recipe__name")


@admin.register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields = (
        "name",
        "measurement_unit",
    )
    list_filter = (
        "name",
        "measurement_unit",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = (
        "user__username",
        "recipe__name",
    )
    list_filter = (
        "user__username",
        "recipe__name",
    )
