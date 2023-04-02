from http import HTTPStatus

from django.shortcuts import get_object_or_404
from django.db import models
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenDestroyView
from recipes.models import Ingredient, Recipe, Tag
from djoser import utils
from users.models import User, Subscription
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (ExtendedRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          TagSerializer, SubscribeSerializer)
from .serializers import SubscriptionSerializer
from .utils import get_shopping_list, render_pdf_response
from rest_framework.decorators import api_view, permission_classes


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


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def subscribe(request, pk):
    user = get_object_or_404(User, id=request.user.id)
    author = get_object_or_404(User, id=pk)

    if request.method == 'POST':
        data = {
            'user': user.id,
            'author': author.id
        }

        serializer = SubscribeSerializer(
            data=data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        subscriptions = User.objects.all().filter(id=author.id)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data, status=HTTPStatus.CREATED)

    if request.method == 'DELETE':
        subscription = Subscription.objects.filter(
            user=user,
            author=author
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        content = {'errors': 'Подписка на автора не оформлена.'}
        return Response(content, status=HTTPStatus.BAD_REQUEST)

    return Response(status=HTTPStatus.BAD_REQUEST)


class SubscriptionListViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    filters = (SearchFilter,)
    permission_classes = (IsAuthenticated,)
    search_fields = ('^following__user')
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(subscribed_to__user=user)


class CustomTokenDestroyView(TokenDestroyView):

    def post(self, request):
        utils.logout_user(request)
        return Response(status=HTTPStatus.NO_CONTENT)
