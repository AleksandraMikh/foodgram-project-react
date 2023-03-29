from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


# Create your models here.
class Tag(models.Model):
    '''model for tags'''

    name = models.CharField('Название',
                            max_length=200,
                            blank=False, null=False,
                            unique=True)
    color = models.CharField('Цвет', max_length=7)
    slug = models.SlugField('Slug', max_length=200,
                            blank=False, null=False,
                            unique=True,
                            )

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Тэги"
        verbose_name = "Тэг"


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200,
                            blank=False, null=False)
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=200, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               blank=False, null=False
                               )
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='recipes/images/',
                              null=True
                              )
    name = models.CharField(verbose_name='Название', max_length=200,
                            blank=False, null=False)
    text = models.TextField(verbose_name='Описание', blank=False, null=False)
    cooking_time = models.IntegerField(verbose_name='Время приготовления',
                                       blank=False, null=False,
                                       validators=[
                                           MinValueValidator(1)
                                       ]
                                       )
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes_with_ingredient',
        blank=False)
    users_favorited_currents_recipe = models.ManyToManyField(
        User,
        verbose_name='Добавили в избранное',
        related_name='favorite_recipes', blank=True)
    users_added_recipe_to_cart = models.ManyToManyField(
        User,
        verbose_name='Добавили в корзину',
        related_name='recipes_in_cart', blank=True)
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    def count_users_loved_recipe(self) -> int:
        if not self.users_favorited_currents_recipe:
            return 0
        return len(self.users_favorited_currents_recipe.all())

    count_users_loved_recipe.short_description = ('Сколько пользователей'
                                                  ' добавили рецепт'
                                                  ' в избранное')

    class Meta:
        ordering = ["-pub_date"]
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"


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
