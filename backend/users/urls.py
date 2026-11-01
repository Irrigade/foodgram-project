# backend/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscribeView, CustomUserViewSet, SubscriptionListView

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('users/subscriptions/', SubscriptionListView.as_view(), name='subscriptions'),
    path('users/set_password/', CustomUserViewSet.as_view({'post': 'set_password'}), name='set-password'),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('', include(router.urls)),
]