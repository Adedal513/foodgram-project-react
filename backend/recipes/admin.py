from django.contrib import admin

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Favourite
)


class IngredientRecipeInline(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


class TagRecipeInline(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'image', 'cooking_time')
    search_fields = ('name', 'text')
    inlines = (IngredientRecipeInline, TagRecipeInline)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
