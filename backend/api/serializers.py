from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.models import AbstractUser
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
import rest_framework.serializers
from rest_framework.serializers import ModelSerializer
from users.models import Subscribe
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredients,
    Favourite,
    ShoppingCart
)


User = get_user_model()


class CustomUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        

class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientsSerializer(ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = SerializerMethodField(
        name='ingredients'
    )
    is_favourite = SerializerMethodField(
        name='is_favourite'
    )
    is_in_shopping_cart = SerializerMethodField(
        name='is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'image',
            'cooking_time',
            'ingredients',
            'tags',
            'is_favourite',
            'is_in_shopping_cart'
        )

    def ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)

        return serializer.data

    def is_favourite(self, obj):
        user: AbstractUser = self.context['request'].user
        if user.is_anonymous:
            return None

        return Favourite.objects.filter(user=user, recipe=obj).exists()

    def is_in_shopping_cart(self, obj):
        user: AbstractUser = self.context['request'].user
        if user.is_anonymous:
            return None

        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

class RecipeWriteSerializer(ModelSerializer):


class IngredientRecipeWriteSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')