from django.urls import include, path
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter

from .views import CustomTokenDestroyView, SubscriptionListViewSet, subscribe

app_name = 'users'


router = DefaultRouter()

router.register(
    r'users/subscriptions',
    SubscriptionListViewSet,
    basename='subscriptions'
)

urlpatterns = [
    path('users/<int:pk>/subscribe/',
         subscribe,
         name='follow-author'),
    path(r'', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/',
         TokenCreateView.as_view(),
         name='login'),
    path('auth/token/logout/',
         CustomTokenDestroyView.as_view(),
         name='logout')
]