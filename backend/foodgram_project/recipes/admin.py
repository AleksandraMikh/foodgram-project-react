from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Tag, Recipe, Ingredient
from users.admin import UserAdmin


class IngredientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through


class FavoriteInlineAdmin(admin.TabularInline):
    model = Recipe.users_favorited_currents_recipe.through


class CartInlineAdmin(admin.TabularInline):
    model = Recipe.users_added_recipe_to_cart.through


User = get_user_model()


class UserAdminWithRecipes(UserAdmin):
    save_on_top = True
    inlines = (FavoriteInlineAdmin, CartInlineAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ['name', 'author', 'tags']
    search_fields = ['name', 'author', 'tags']
    readonly_fields = ('count_users_loved_recipe',)
    fields = ('count_users_loved_recipe', 'name',
              'author', 'image', 'text',
              'cooking_time',
              'tags',
              )
    save_on_top = True
    inlines = (IngredientInlineAdmin,)

    def has_add_permission(self, request, obj=None):
        return False


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ['name']
    search_fields = ['name']


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(User, UserAdminWithRecipes)
