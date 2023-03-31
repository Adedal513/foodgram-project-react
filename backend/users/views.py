from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.views import TokenDestroyView
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Subscription
from .pagination import LimitPageNumberPagination
from .serializers import SubscriptionSerializer

User = get_user_model()


@api_view(['POST', 'DELETE'])
@permission_classes((permissions.IsAuthenticated,))
def subscribe(request, pk):
    user = get_object_or_404(User, id=request.user.id)
    author = get_object_or_404(User, id=pk)

    if request.method == 'POST':
        if user.id == author.id:
            content = {
                'errors': 'Нельзя подписаться на самого себя.'
            }
            return Response(content, status=HTTPStatus.BAD_REQUEST)
        try:
            Subscription.objects.create(user=user, author=author)
        except IntegrityError:
            content = {'errors': 'Нельзя подписаться дважды.'}
            return Response(content, status=HTTPStatus.BAD_REQUEST)

        subscriptions = User.objects.all().filter(id=author.id)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data, status=HTTPStatus.CREATED)

    if request.method == 'DELETE':
        try:
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
        except ObjectDoesNotExist:
            content = {'errors': 'Подписка на автора не оформлена.'}
            return Response(content, status=HTTPStatus.BAD_REQUEST)

        subscription.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    return Response(status=HTTPStatus.BAD_REQUEST)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    filters = (filters.SearchFilter,)
    permission_classes = (permissions.IsAuthenticated,)
    search_fields = ('^following__user')
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(subscribed_to__user=user)


class CustomTokenDestroyView(TokenDestroyView):

    def post(self, request):
        utils.logout_user(request)
        return Response(status=HTTPStatus.NO_CONTENT)
