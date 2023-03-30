from django.http import Http404

from rest_framework import serializers, exceptions
from django.contrib.auth.models import AnonymousUser
from rest_framework.fields import CurrentUserDefault

from recipes.models import Tag, Ingredient, Recipe, Ingredient_Recipe
from users.serializers import UserCreateSerializer


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


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=True)
    author = UserCreateSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='ingredient_recipe', many=True,
        read_only=True)

    class Meta:
        model = Recipe
        fields = ["id",
                  "tags",
                  "author",
                  "ingredients",
                  #   "is_favorited",
                  #   "is_in_shopping_cart",
                  "name",
                  "image",
                  "text",
                  "cooking_time"]
        depth = 1

    # def validate_tags(self, value):
    #     for tag in value:
    #         if type(tag) != int:
    #             raise exceptions.ValidationError(
    #                 'Tags key must contain list of integers')
    #     return value
    # def validate_tags(self, data):
    #     if "tags" not in data:
    #         raise exceptions.ValidationError(
    #             'Tags key required')
    #     tags = data.pop("tags")

    #     for tag in tags:
    #         if type(tag) != int:
    #             raise exceptions.ValidationError(
    #                 'Tags key must contain list of integers')
    #     return tags, data

    # def validate_ingredients(self, data):
    #     if "ingredients" not in data:
    #         raise exceptions.ValidationError(
    #             'Ingredients key required')
    #     ingredients = data.pop("ingredients")
    #     for ingredient in ingredients:
    #         if (type(ingredient['id']) != int or
    #                 type(ingredient['amount']) != int):
    #             raise exceptions.ValidationError(
    #                 'Ingredients key must contain '
    #                 'dictionary with integer values')
    #     return ingredients, data

    # def to_internal_value(self, data):
        # tags, data = self.validate_tags(data)
        # ingredients, data = self.validate_ingredients(data)

        # validated_data = super().to_internal_value(data)
        # validated_data['tags'] = tags
        # validated_data['ingredients'] = ingredients
        # return validated_data

    # def create(self, validated_data):

    #     # print(validated_data)
    #     # print(self.context.get('request').user)

    #     tags = validated_data.pop("tags")

    #     ingredients = validated_data.pop("ingredients")

    #     r = Recipe(**validated_data)
    #     if self.context.get('request').user is AnonymousUser:
    #         raise exceptions.NotAuthenticated()
    #     r.author = self.context.get('request').user
    #     r.save()
    #     for tag in tags:
    #         try:
    #             t = Tag.objects.get(pk=tag)
    #             print(t)
    #         except Tag.DoesNotExist:
    #             raise Http404(f'Tag with id {tag} not found.')
    #         r.tags.add(t)

    #     for ingredient in ingredients:
    #         try:
    #             i = Ingredient.objects.get(pk=ingredient['id'])
    #         except Ingredient.DoesNotExist:
    #             raise Http404
    #         i_s = Ingredient_Recipe(ingredient=i,
    #                                 recipe=r,
    #                                 amount=ingredient['amount'])
    #         i_s.save()
    #     r.save()
    #     return r
