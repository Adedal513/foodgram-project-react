from http import HTTPStatus

from django.db import models
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (ExtendedRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          TagSerializer)
from .utils import get_shopping_list, render_pdf_response


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ExtendedRecipeSerializer
        return RecipeCreateSerializer

    def _add_to(self, target_related_manager: models.Manager):
        recipe = self.get_object()

        if self.request.method == 'POST':
            try:
                target_related_manager.create(recipe=recipe)
            except Exception:
                content = {'errors': 'Error adding recipe.'}
                return Response(content, status=HTTPStatus.BAD_REQUEST)
            serializer = RecipeSerializer(
                instance=recipe,
                context={'request': self.request}
            )

            return Response(
                serializer.data,
                status=HTTPStatus.CREATED,
            )
        if self.request.method == 'DELETE':
            target_related_manager.get(recipe_id=recipe.id).delete()
            return Response(
                status=HTTPStatus.NO_CONTENT
            )

        return Response(HTTPStatus.BAD_REQUEST)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('POST', 'DELETE',)
    )
    def favorite(self, request, pk):
        return self._add_to(
            self.request.user.favorite
        )

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('POST', 'DELETE'),
    )
    def shopping_cart(self, request, pk):
        return self._add_to(
            self.request.user.shopping_user
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = get_shopping_list(self.request.user)
        html_template = render_to_string(
            'recipes/shopping_list.html',
            {'ingredients': ingredients}
        )

        return render_pdf_response(html_template)
