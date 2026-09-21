from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny

from .models import CatalogItem
from .serializers import CatalogItemSerializer, PublicCatalogItemSerializer


class CatalogItemViewSet(viewsets.ModelViewSet):
    queryset = CatalogItem.objects.all()
    serializer_class = CatalogItemSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-created_at",)


class PublicCatalogItemViewSet(viewsets.ReadOnlyModelViewSet):
    # публичный доступ без авторизации, только опубликованные элементы
    permission_classes = [AllowAny]
    serializer_class = PublicCatalogItemSerializer
    queryset = CatalogItem.objects.filter(is_public=True)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-created_at",)
