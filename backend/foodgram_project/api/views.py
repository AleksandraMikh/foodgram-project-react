from rest_framework import viewsets, permissions, filters


from recipes.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer)


# Create your views here.

class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all().select_related()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     if self.action in ['PATCH', 'UPDATE']:
    #         context["recipe"] = kwargs['request']['id']
    #     return context

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        if self.action == 'create':
            return RecipeWriteSerializer
