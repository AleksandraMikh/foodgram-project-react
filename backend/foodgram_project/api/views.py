from rest_framework import viewsets, permissions

from recipes.models import Tag
from .serializers import TagSerializer


# Create your views here.

class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
