from django.urls import include, path
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter

from .views import (CustomTokenDestroyView, IngredientViewSet, RecipeViewSet,
                    SubscriptionListViewSet, TagViewSet, subscribe)

app_name = 'api'

router = DefaultRouter()

router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'users/subscriptions',
    SubscriptionListViewSet,
    basename='subscriptions'
)

urlpatterns = [
    path(r'', include(router.urls)),
    path('auth/token/login/',
         TokenCreateView.as_view(),
         name='login'),
    path('auth/token/logout/',
         CustomTokenDestroyView.as_view(),
         name='logout'),
    path('users/<int:pk>/subscribe/',
         subscribe,
         name='follow-author'),
    path('', include('djoser.urls')),
]
