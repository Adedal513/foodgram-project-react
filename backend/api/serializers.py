from django.contrib.auth.models import AbstractBaseUser
from django.db.models import F
from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription, User
from djoser.serializers import UserCreateSerializer, UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'author',
            'image',
            'ingredients',
            'tags'
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                'Необходимо выбрать ингредиенты.'
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Объем ингредиента должен быть >= 0.'
                )
        ids = [item['id'] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise ValidationError(
                'Ингредиенты в рецепте должны быть уникальными.'
            )
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0 мин.'
            )

        return cooking_time

    def _create_ingredients(self, ingredients, recipe):
        recipe_ingredients = {}
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']

            if ingredient_id in recipe_ingredients:
                recipe_ingredients[ingredient_id].amount += F('amount')
            else:
                recipe_ingredients[ingredient_id] = RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_id,
                    amount=amount
                )

        RecipeIngredient.objects.bulk_create(
            list(recipe_ingredients.values())
        )

    def create(self, validated_data):
        author = self.context.get('request').user

        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')

        recipe = Recipe.objects.create(
            image=image,
            author=author,
            **validated_data
        )

        self._create_ingredients(ingredients_data, recipe)

        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        self._create_ingredients(ingredients, instance)

        instance.tags.set(tags)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ExtendedRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}).data


class FavouriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True
    )

    class Meta:
        model = Favourite
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']

        if user.favorite.filter(recipe=recipe).exists():
            raise ValidationError('Нельзя добавить в Избранное дважды.')

        return data


class ShoppingCartSertializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']

        if user.shopping_user.filter(recipe=recipe).exists():
            raise ValidationError('Нельзя добавить в список покупок дважды.')

        return data


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        author = data['author']

        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')

        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user

        if not request or request.user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()

        context = {'request': request}

        return SubscriptionRecipeSerializer(
            recipes,
            many=True,
            context=context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ExtendedRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'cooking_time',
            'text',
            'image',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    @staticmethod
    def get_ingredients(obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)

        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user: AbstractBaseUser = self.context.get('request').user

        if user.is_anonymous:
            return False

        if Favourite.objects.filter(user=user, recipe=obj).exists():
            return True

        return False

    def get_is_in_shopping_cart(self, obj):
        user: AbstractBaseUser = self.context.get('request').user

        if user.is_anonymous:
            return False

        if ShoppingCart.objects.filter(user=user, recipe=obj):
            return True

        return False
