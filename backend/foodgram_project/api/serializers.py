import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from rest_framework import serializers, exceptions
from django.contrib.auth.models import AnonymousUser
from rest_framework.fields import CurrentUserDefault

from recipes.models import Tag, Ingredient, Recipe, Ingredient_Recipe
from users.serializers import UserManageSerializer

User = get_user_model()


class DoubleIngredientRecipeRelationship(exceptions.APIException):
    status_code = 400
    default_detail = ('Integrity error, there might be '
                      'duplicate ingredient in request.')
    default_code = 'bad_request'


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
    author = UserManageSerializer(read_only=True)
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
        if not self.context.get('request').auth:
            return None
        if hasattr(obj, 'is_favorited'):
            return obj.is_favorited
        curr_user = self.context.get('request').user
        if obj in curr_user.favorite_recipes.all():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if not self.context.get('request').auth:
            return None
        if hasattr(obj, 'is_in_shopping_cart'):
            return obj.is_in_shopping_cart
        curr_user = self.context.get('request').user
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
            r.tags.add(t)

        ingredients_to_add = []
        for ingredient in ingredients:
            try:
                i = Ingredient.objects.get(pk=ingredient['ingredient']['id'])
            except Ingredient.DoesNotExist:
                raise exceptions.NotFound(
                    f"Ingredient with id {ingredient['ingredient']['id']} doesn't exist")
            i_s = Ingredient_Recipe(ingredient=i,
                                    recipe=r,
                                    amount=ingredient['amount'])
            ingredients_to_add.append(i_s)
        try:
            Ingredient_Recipe.objects.bulk_create(ingredients_to_add)
        except IntegrityError:
            raise DoubleIngredientRecipeRelationship()

        return r

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredient_recipe")

        instance = super().update(instance, validated_data)

        ingredients_to_add = []
        for ingredient in ingredients:
            try:
                i = Ingredient.objects.get(pk=ingredient['ingredient']['id'])
            except Ingredient.DoesNotExist:
                raise exceptions.NotFound(
                    f"Ingredient with id {ingredient['ingredient']['id']} doesn't exist")
            i_s = Ingredient_Recipe(ingredient=i,
                                    recipe=instance,
                                    amount=ingredient['amount'])
            ingredients_to_add.append(i_s)

        Ingredient_Recipe.objects.filter(recipe=instance).delete()
        try:
            Ingredient_Recipe.objects.bulk_create(ingredients_to_add)
        except IntegrityError:
            raise DoubleIngredientRecipeRelationship()
        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id",
                  "name",
                  "image",
                  "cooking_time"]


class UserSubscribeSerializer(UserManageSerializer):
    recipes = RecipeMinifiedSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count']

    def get_recipes_count(self, obj):
        if hasattr(obj, 'recipes'):
            return len(obj.recipes.all())
        raise TypeError('Serializer excpected object of'
                        ' type User with attribute "recipes", '
                        f'but got {type(obj)} without attribute "recipes"')
