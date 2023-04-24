import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions

from recipes.models import (Tag, Ingredient, Recipe,
                            Ingredient_Recipe, Favorite, Cart)
from users.serializers import UserManageSerializer

User = get_user_model()


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
        source='ingredient.measurement_unit',
        read_only=True
    )

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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Cart.objects.filter(user=user, recipe=obj).exists()


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

    def is_valid(self, **kwargs):
        for ingredient_item in self.initial_data['ingredients']:
            if int(ingredient_item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients': [(
                        'Убедитесь, что количество каждого ингредиента'
                        ' не меньше 1'
                    )]
                })
        return super().is_valid(**kwargs)

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError(
                'Нужен минимум один ингредиент для рецепта')

        ingredient_list = []
        ingredient_id_list = []
        for ingredient_item in data:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_item['ingredient']['id']
            )
            if ingredient.id in ingredient_id_list:
                raise serializers.ValidationError(
                    'Названия ингредиентов должны быть уникальными'
                )
            ingredient_list.append({
                'ingredient': ingredient,
                'amount': ingredient_item['amount']}
            )
            ingredient_id_list.append(ingredient.id)
        return ingredient_list

    def create_ingredients(self, ingredients, recipe):
        obj = [
            Ingredient_Recipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]

        Ingredient_Recipe.objects.bulk_create(obj)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)


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
