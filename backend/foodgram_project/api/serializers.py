import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse

from rest_framework import serializers, exceptions
from django.contrib.auth.models import AnonymousUser
from rest_framework.fields import CurrentUserDefault

from recipes.models import Tag, Ingredient, Recipe, Ingredient_Recipe
from users.serializers import UserCreateSerializer


class notMatchingQuery(exceptions.ValidationError):
    pass


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["id",
                  "name",
                  "color",
                  "slug"]
        extra_kwargs = {"name": {"read_only": True},
                        "color": {"read_only": True},
                        "slug": {"read_only": True}}


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ["id",
                  "name",
                  "measurement_unit"]


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = Ingredient_Recipe
        fields = ["id",
                  "name",
                  "measurement_unit",
                  "amount"]


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=True)
    author = UserCreateSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='ingredient_recipe', many=True,
        read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ["id",
                  "tags",
                  "author",
                  "ingredients",
                  "is_favorited",
                  "is_in_shopping_cart",
                  "name",
                  "image",
                  "text",
                  "cooking_time"]
        depth = 1

    def get_is_favorited(self, obj):
        curr_user = self.context.get('request').user
        if not self.context.get('request').auth:
            return None
        if obj in curr_user.favorite_recipes.all():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        curr_user = self.context.get('request').user
        if not self.context.get('request').auth:
            return None
        if obj in curr_user.recipes_in_cart.all():
            return True
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=True
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientRecipeSerializer(
        source='ingredient_recipe', many=True,
        required=True)

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time"]
        depth = 1

    def create(self, validated_data):

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredient_recipe")
        r = Recipe(**validated_data)
        r.save()
        for tag in tags:
            try:
                t = Tag.objects.get(pk=tag)
            except Tag.DoesNotExist:
                raise exceptions.NotFound(
                    f"Tag with id {tag} doesn't exist")
            t = get_object_or_404(Tag, pk=tag)
            r.tags.add(t)

        for ingredient in ingredients:
            try:
                i = Ingredient.objects.get(pk=ingredient['ingredient']['id'])
            except Ingredient.DoesNotExist:
                raise exceptions.NotFound(
                    f"Ingredient with id {ingredient['ingredient']['id']} doesn't exist")
            i_s = Ingredient_Recipe(ingredient=i,
                                    recipe=r,
                                    amount=ingredient['amount'])
            i_s.save()
        r.save()
        return r
