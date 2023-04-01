from django.db import models
from rest_framework import viewsets, permissions, filters, response, status

from recipes.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          notMatchingQuery)


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

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        if self.action == 'create':
            return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except notMatchingQuery as err:
            return response.Response({'detail': err},
                                     status=status.HTTP_404_NOT_FOUND)

        instance = self.perform_create(serializer)

        resp_serializer = RecipeReadSerializer(
            instance, context=serializer.context)
        print(resp_serializer.data)
        headers = self.get_success_headers(resp_serializer.data)

        return response.Response(resp_serializer.data,
                                 status=status.HTTP_201_CREATED,
                                 headers=headers
                                 )

    def perform_create(self, serializer):
        instance = serializer.save()
        return instance
