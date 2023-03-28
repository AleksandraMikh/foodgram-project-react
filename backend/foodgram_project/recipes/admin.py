from django.contrib import admin
from .models import Tag, Recipe, Ingredient
# Register your models here.


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ['name', 'author', 'tags']
    search_fields = ['name', 'author', 'tags']
    readonly_fields = ('count_users_loved_recipe',)
    fields = ('count_users_loved_recipe', 'name',
              'author', 'image', 'text', 'cooking_time',
              'tags', 'users_favorited_currents_recipe',
              'users_added_recipe_to_cart')

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
