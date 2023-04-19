import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, SimpleDocTemplate, TableStyle
from reportlab.lib import colors
from django.db import models
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import (viewsets,
                            permissions,
                            filters,
                            response,
                            status,
                            exceptions)
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from django_filters import (rest_framework as rest_filters,
                            FilterSet, TypedChoiceFilter,
                            ModelMultipleChoiceFilter)
from distutils.util import strtobool

from recipes.models import (Tag, Ingredient, Recipe, Ingredient_Recipe,
                            Favorite,
                            Cart)
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          RecipeMinifiedSerializer,
                          UserSubscribeSerializer
                          )
from .permissions import IsOwnerOrReadOnly

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

    is_favorited = TypedChoiceFilter(choices=BOOLEAN_CHOICES,
                                     coerce=strtobool)
    is_in_shopping_cart = TypedChoiceFilter(choices=BOOLEAN_CHOICES,
                                            coerce=strtobool)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all().select_related()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]
    filter_backends = (rest_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=models.Exists(Recipe.objects.none()))
            queryset = queryset.annotate(
                is_in_shopping_cart=models.Exists(Recipe.objects.none()))
            return queryset
        subquery_fav = Favorite.objects.filter(
            user=self.request.user,
            recipe_id=models.OuterRef('pk'))
        subquery_cart = Cart.objects.filter(
            user=self.request.user,
            recipe_id=models.OuterRef('pk'))
        fav_queryset = queryset.annotate(
            is_favorited=models.Exists(subquery_fav))
        fin_queryset = fav_queryset.annotate(
            is_in_shopping_cart=models.Exists(subquery_cart))
        return fin_queryset

    def get_serializer_class(self):
        print('hihi')
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
            serializer_class=RecipeMinifiedSerializer)
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
        return response.Response(RecipeMinifiedSerializer(recipe).data,
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

    @action(detail=True, methods=['post'],
            serializer_class=RecipeMinifiedSerializer)
    def shopping_cart(self, request, pk=None):
        try:
            recipe = get_object_or_404(Recipe,
                                       pk=pk)
        except Http404:
            return response.Response({
                "errors": f"Рецепт с id = {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST)
        curr_user = request.user
        if recipe in curr_user.recipes_in_cart.all():
            return response.Response({
                "errors": f"Рецепт с id={pk} уже добавлен в корзину"},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            curr_user.recipes_in_cart.add(recipe)
        except exceptions.APIException as error:
            return response.Response({
                "errors": error},
                status=status.HTTP_400_BAD_REQUEST)
        return response.Response(RecipeMinifiedSerializer(recipe).data,
                                 status=status.HTTP_200_OK)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        try:
            recipe = get_object_or_404(Recipe,
                                       pk=pk)
        except Http404:
            return response.Response({
                "errors": f"Рецепт с id = {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST)
        curr_user = request.user
        if recipe in curr_user.recipes_in_cart.all():
            curr_user.recipes_in_cart.remove(recipe)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response({
            "errors": (f'Текущий пользователь не добавлял рецепт с id={pk} '
                       'в корзину.')},
            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request, *args, **kwargs):
        buffer = io.BytesIO()

        pdfmetrics.registerFont(
            TTFont('TimesNewRoman', 'static/api/fonts/times new roman.ttf'))
        recipes = request.user.recipes_in_cart.all()
        queryset = Ingredient_Recipe.objects.filter(
            recipe__in=recipes).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=models.Sum('amount'))
        content = [('ингредиент', 'количество', 'единица измерения'), ]
        for item in queryset:
            print(item)
            content.append(
                (item['ingredient__name'],
                 item['amount'],
                 item['ingredient__measurement_unit']))

        doc = SimpleDocTemplate(buffer)
        t = Table(content)

        # LIST_STYLE = TableStyle()
        LIST_STYLE = TableStyle(
            [('LINEABOVE', (0, 0), (-1, 0), 2, colors.green),
             ('LINEABOVE', (0, 1), (-1, 1), 2, colors.green),
                ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONT', (0, 0), (-1, -1), 'TimesNewRoman')]
        )

        t.setStyle(LIST_STYLE)
        doc.build([t])

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


@api_view(['DELETE', 'POST'])
def subscribe(request: Request, user_id: str):
    try:
        user_to_subscribe = get_object_or_404(User,
                                              pk=user_id)
    except Http404:
        raise exceptions.NotFound(f"Пользователь с id = {user_id} не найден")

    if request.user.pk == int(user_id):
        return Response({
            "errors": f"Ваш id = {request.user.pk}, подписка на себя "
            "запрещена."},
            status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        if request.user.follow.filter(follow__pk=user_id):
            return Response({
                "errors": f"Вы уже подписаны на пользователя с id = {user_id}"},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.follow.add(user_to_subscribe)
        serializer = UserSubscribeSerializer(
            user_to_subscribe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if not request.user.follow.filter(follow__pk=user_id):
            return Response({
                "errors": f'Вы не подписаны на пользователя с id={user_id}, '
                ' вы не можете отписаться от него'},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.follow.remove(user_to_subscribe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListView(ListAPIView):
    serializer_class = UserSubscribeSerializer

    def get_queryset(self):
        return self.request.user.follow.all()
