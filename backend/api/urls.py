from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsVewSet, RecipeViewSet,
                    TagsViewSet)

app_name: str = "api"

router: DefaultRouter = DefaultRouter()
router.register("tags", TagsViewSet)
router.register("recipes", RecipeViewSet)
router.register("users", CustomUserViewSet, basename="users")
router.register("ingredients", IngredientsVewSet)

urlpatterns: list = [
    path("", include(router.urls)),
]
