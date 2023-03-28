from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


# Create your models here.
class Tag(models.Model):

    name = models.CharField(max_length=200,
                            blank=False, null=False,
                            unique=True)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200,
                            blank=False, null=False,
                            unique=True,
                            )

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False, null=False
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True
    )
    name = models.CharField(max_length=200, blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    cooking_time = models.IntegerField(
        blank=False, null=False,
        validators=[
            MinValueValidator(1)
        ]
    )
    tags = models.ManyToManyField(Tag)
    users_favorited_currents_recipe = models.ManyToManyField(
        User, related_name='favorite_recipes')
    users_added_recipe_to_cart = models.ManyToManyField(
        User, related_name='recipes_in_cart')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    measurement_unit = models.CharField(
        max_length=200, blank=False, null=False)
    recipes = models.ManyToManyField(
        Recipe, through='Ingredient_Recipe', related_name='ingredients')

    def __str__(self):
        return self.name


class Ingredient_Recipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        # blank=False, null=False,
        validators=[
            MinValueValidator(1)
        ],
        default=1)

    class Meta:
        unique_together = [['ingredient', 'recipe']]
