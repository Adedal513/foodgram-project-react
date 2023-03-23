from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint


User = get_user_model()


class Ingredient(models.Model):
    """Модель представления ингридиента."""

    name = models.CharField(
        'Название',
        max_length=256
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=256
    )

    class Meta:
        db_table = 'content\".\"ingridient'
        verbose_name = 'Ингрeдиент'
        verbose_name_plural = 'Ингрeдиенты'

        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=256
    )
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Неверный формат цвета.'
            )
        ]
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=256
    )

    class Meta:
        db_table = 'content\".\"tag'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Модель представления рецепта."""

    name = models.CharField(
        'Название',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Автор'
    )
    text = models.TextField('Описание')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение - 1 мин.')
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        db_table = 'content\".\"recipe'
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        indexes = [
            models.Index(
                fields=['name'],
                name='recipe_name_idx'
                )
        ]

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Модель представления MtM-связи Ингридиента и Рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1, message='Минимальное значение - 1')
        ]
    )

    class Meta:
        db_table = 'content\".\"ingredient_in_recipe'
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return (
            f"""
            {self.ingredient.name}:
            {self.amount} ({self.ingredient.measurement_unit})
            """
        )


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='faurites',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        db_table = 'content\".\"favourite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        db_table = 'content\".\"shopping_cart'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')
        ]
