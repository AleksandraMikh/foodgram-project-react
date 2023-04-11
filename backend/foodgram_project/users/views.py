from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models.query import EmptyQuerySet

from rest_framework import status, serializers, exceptions
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response


User = get_user_model()


@api_view(['DELETE', 'POST'])
def subscribe(request: Request, user_id: str):
    try:
        user_to_subscribe = get_object_or_404(User,
                                              pk=user_id)
    except Http404:
        raise exceptions.NotFound(f"Пользователь с id = {user_id} не найден")
    if request.method == 'POST':
        if request.user.pk == int(user_id):
            return Response({
                "errors": f"Ваш id = {request.user.pk}, нельзя подписаться на себя."},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user.follow.filter(follow__pk=user_id):
            return Response({
                "errors": f"Вы уже подписаны на пользователя с id = {user_id}"},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.follow.add(user_to_subscribe)

        return Response({"message": "Hello for today! See you tomorrow!"})
