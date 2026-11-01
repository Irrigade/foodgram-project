# backend/recipes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, IngredientViewSet, RecipeViewSet, ShoppingCartDownloadView

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingCartDownloadView.as_view(), name='download_shopping_cart'),
    path('', include(router.urls)),
]