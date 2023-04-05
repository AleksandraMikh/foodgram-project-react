from django.db import models
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import viewsets, permissions, filters, response, status, exceptions
from rest_framework.decorators import action

from recipes.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          RecipeFavoriteSerializer
                          )
from .permissions import IsOwnerOrReadOnly


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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer)

        resp_serializer = RecipeReadSerializer(
            instance, context=serializer.context)
        headers = self.get_success_headers(resp_serializer.data)

        return response.Response(resp_serializer.data,
                                 status=status.HTTP_201_CREATED,
                                 headers=headers
                                 )

    def perform_create(self, serializer):
        instance = serializer.save()
        return instance

    def update(self, request, *args, **kwargs):
        return response.Response("Method PUT not allowed, try PATCH",
                                 status=status.HTTP_405_METHOD_NOT_ALLOWED
                                 )

    def partial_update(self, request, *args, **kwargs):

        instance = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer)

        resp_serializer = RecipeReadSerializer(
            instance, context=serializer.context)
        headers = self.get_success_headers(resp_serializer.data)
        return response.Response(resp_serializer.data,
                                 status=status.HTTP_200_OK,
                                 headers=headers
                                 )

    @action(detail=True, methods=['post'],
            serializer_class=RecipeFavoriteSerializer)
    def favorite(self, request, pk=None):
        try:
            recipe = get_object_or_404(Recipe,
                                       pk=pk)
        except Http404:
            return response.Response({
                "errors": f"Рецепт с id = {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST)
        curr_user = request.user
        if recipe in curr_user.favorite_recipes.all():
            return response.Response({
                "errors": f"Рецепт с id={pk} уже добавлен в избранные"},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            curr_user.favorite_recipes.add(recipe)
        except exceptions.APIException as error:
            return response.Response({
                "errors": error},
                status=status.HTTP_400_BAD_REQUEST)
        return response.Response(RecipeFavoriteSerializer(recipe).data,
                                 status=status.HTTP_200_OK)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        try:
            recipe = get_object_or_404(Recipe,
                                       pk=pk)
        except Http404:
            return response.Response({
                "errors": f"Рецепт с id = {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST)
        curr_user = request.user
        if recipe in curr_user.favorite_recipes.all():
            curr_user.favorite_recipes.remove(recipe)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response({
            "errors": (f'Текущий пользователь не добавлял рецепт с id={pk} '
                       'в список избранных.')},
            status=status.HTTP_400_BAD_REQUEST)
