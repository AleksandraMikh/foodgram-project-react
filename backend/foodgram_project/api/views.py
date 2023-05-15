from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import OuterRef, Exists
from rest_framework import (viewsets,
                            permissions,
                            filters,
                            response,
                            status,
                            exceptions)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django_filters import (rest_framework as rest_filters,
                            FilterSet, TypedChoiceFilter,
                            ModelMultipleChoiceFilter)
from distutils.util import strtobool
from djoser.views import UserViewSet
from users.models import Follow
from foodgram_project import pagination
from recipes.models import (Tag, Ingredient, Recipe,
                            Favorite,
                            Cart)

from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          RecipeMinifiedSerializer,
                          UserSubscribeSerializer
                          )
from .permissions import IsOwnerOrReadOnly
from .utils import pdf_maker

User = get_user_model()

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


BOOLEAN_CHOICES = (('0', 'False'), ('1', 'True'),)


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=True)

    is_in_shopping_cart = TypedChoiceFilter(choices=BOOLEAN_CHOICES,
                                            coerce=strtobool,
                                            method='filter_is_in_shopping_cart'
                                            )
    is_favorited = TypedChoiceFilter(choices=BOOLEAN_CHOICES,
                                     coerce=strtobool,
                                     method='filter_is_favorited'
                                     )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 0:
            return queryset
        cart_sub = Cart.objects.filter(user=self.request.user,
                                       recipe__pk=OuterRef('pk'))
        return queryset.filter(Exists(cart_sub))

    def filter_is_favorited(self, queryset, name, value):
        if value == 0:
            return queryset
        fav_sub = Favorite.objects.filter(user=self.request.user,
                                          recipe__pk=OuterRef('pk'))
        return queryset.filter(Exists(fav_sub))

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all().select_related()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]
    filter_backends = (rest_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        raise NotImplementedError(
            'RecipeViewSet works only with actions list, retrieve, create, '
            'partial update')

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
        return serializer.save()

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

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors':
                f'Рецепт уже добавлен в список {model._meta.verbose_name}'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Http404:
            return response.Response({
                "errors": f"Рецепт с id = {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Http404:
            return response.Response({
                "errors": f"Рецепт с id = {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': f'Рецепт уже удален из списка {model._meta.verbose_name}'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            serializer_class=RecipeMinifiedSerializer)
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['post', 'delete'],
            serializer_class=RecipeMinifiedSerializer)
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(Cart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(Cart, request.user, pk)
        return None

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request, *args, **kwargs):
        return pdf_maker(request=request)


class CustomUserViewSet(UserViewSet):

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request: Request, id: int = None):
        try:
            user_to_subscribe = get_object_or_404(User,
                                                  pk=id)
        except Http404:
            raise exceptions.NotFound(
                f"Пользователь с id = {id} не найден")

        if request.user.pk == id:
            return Response({
                "errors": f"Ваш id = {request.user.pk}, подписка на себя "
                "запрещена."},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if Follow.objects.filter(user=request.user,
                                     author=user_to_subscribe).exists():
                return Response({
                    "errors": f"Вы уже подписаны на пользователя с id = {id}"},
                    status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=request.user,
                                  author=user_to_subscribe)
            serializer = UserSubscribeSerializer(
                user_to_subscribe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            try:
                follow = get_object_or_404(Follow,
                                           user=request.user,
                                           author=user_to_subscribe)
            except Http404:
                return Response({
                    "errors": f'Вы не подписаны на пользователя с id={id}, '
                    ' вы не можете отписаться от него'},
                    status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise NotImplementedError(
            'CustomUserViewSet done for POST and DELETE methods')

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=pagination.CustomPagination
    )
    def subscriptions(self, request):
        queryset = request.user.follow.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscribeSerializer(
                page, context={'request': request}, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = UserSubscribeSerializer(
            queryset, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
