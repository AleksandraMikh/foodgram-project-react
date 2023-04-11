from django.urls import path, include

from .views import TagViewSet, IngredientViewSet, RecipeViewSet
from rest_framework.routers import DefaultRouter

app = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include('users.urls')),

]

urlpatterns.extend(router.urls)
