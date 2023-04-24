from .views import (TagViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    CustomUserViewSet)
from rest_framework.routers import DefaultRouter


app = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = router.urls
