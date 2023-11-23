import io
import os

from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavouriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import CurrentUserOnly, RecipePermission
from .serializers import (CustomUserCreateSerializer, IngredientSerialiser,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShortRecipeSerializer, SubscriptionSerializer,
                          TagsSerializer)

User = get_user_model()

FILENAME = "shoppingcart.pdf"


class CustomUserCreateView(CreateAPIView):
    serializer_class = CustomUserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (RecipePermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.add_to(FavouriteRecipe, request.user, pk)
        return self.delete_from(FavouriteRecipe, request.user, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.add_to(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    @staticmethod
    def create_shopping_cart_pdf(request):
        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        x_position, y_position = 50, 800
        file_path = os.path.abspath("./data/")
        pdfmetrics.registerFont(TTFont("firstime",
                                       f"{file_path}/FirstTimeWriting.ttf"))
        page.setFont("firstime", 15)
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name",
                    "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        if ingredients:
            indent = 20
            page.drawString(x_position, y_position, "Продукты:")
            for index, ingredient in enumerate(ingredients, start=1):
                page.drawString(
                    x_position,
                    y_position - indent,
                    f'{index}. {ingredient["ingredient__name"]} - '
                    f'{ingredient["amount"]} '
                    f'{ingredient["ingredient__measurement_unit"]}.',
                )
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=FILENAME)
        page.drawString(
            x_position, y_position, "Список пуст"
        )
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=False, filename=FILENAME)

    @action(
        detail=False, methods=["get"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request) -> FileResponse:
        return self.create_shopping_cart_pdf(request)

    @staticmethod
    def add_to(model, user: User, pk: int) -> Response:
        """Add object to model."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "Рецепт уже добавлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {"errors": "Такого рецепта не существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = Recipe.objects.get(id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_from(model, user: User, pk: int) -> Response:
        """Delete a recipe from model."""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "В вашем списке такого рецепта нет."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class IngredientsVewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for ingredients."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class CustomUserViewSet(UserViewSet):
    """Viewset for users."""
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscriptionSerializer,
    )
    def subscriptions(self, request):
        """Get subscriptions list."""
        user = self.request.user
        user_subscriptions = user.follower.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscriptionSerializer,
    )
    def subscribe(self, request, id=None):
        """Set subscription to author."""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == "POST":
            if user == author:
                raise exceptions.ValidationError(
                    "Подписка на самого себя запрещена."
                )
            if Follow.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError("Подписка уже оформлена.")
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not Follow.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError(
                    "Подписка не была оформлена, либо уже удалена."
                )
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(CurrentUserOnly,),
    )
    def me(self, request):
        """GET http method for api/users/me."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
