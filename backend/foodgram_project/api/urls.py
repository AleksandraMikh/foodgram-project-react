from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (TagViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    CustomUserViewSet)


app = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = router.urls

urlpatterns.append(
    path('auth/', include('djoser.urls.authtoken')))
