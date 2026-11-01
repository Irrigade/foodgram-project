# backend/users/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.core.files.base import ContentFile
import base64
import uuid

from .models import User, Subscription
from .serializers import (
    UserCreateSerializer, UserListSerializer, UserSerializer,
    SubscriptionUserSerializer
)
from djoser.views import UserViewSet as DjoserUserViewSet


class CustomUserViewSet(DjoserUserViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'retrieve':
            return UserListSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['put', 'delete'], permission_classes=[permissions.IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            if avatar_data and isinstance(avatar_data, str) and avatar_data.startswith('data:image'):
                format, imgstr = avatar_data.split(';base64,')
                ext = format.split('/')[-1]
                file_name = f'{uuid.uuid4()}.{ext}'
                data = ContentFile(base64.b64decode(imgstr), name=file_name)
                user.avatar.save(file_name, data, save=True)
                return Response({'avatar': user.avatar.url}, status=status.HTTP_200_OK)
            return Response({'errors': 'Поле avatar обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        if user.avatar:
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Аватар не установлен'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='set_password')
    def set_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'errors': 'current_password и new_password обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user.check_password(current_password):
            return Response({'errors': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if author == request.user:
            return Response({'errors': 'Нельзя подписаться на себя'}, status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscription.objects.get_or_create(user=request.user, author=author)
        if not created:
            return Response({'errors': 'Вы уже подписаны'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionUserSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, id=pk)
        subscription = Subscription.objects.filter(user=request.user, author=author).first()
        if not subscription:
            return Response({'errors': 'Вы не подписаны'}, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [sub.author for sub in subscriptions]
        
        paginator = LimitOffsetPagination()
        paginator.default_limit = 6
        result_page = paginator.paginate_queryset(authors, request)
        
        serializer = SubscriptionUserSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)