from django.urls import path, include

from .views import TagViewSet
from rest_framework.routers import DefaultRouter

app = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include('users.urls')),
]

urlpatterns.extend(router.urls)
