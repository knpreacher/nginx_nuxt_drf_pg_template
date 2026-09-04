from rest_framework import serializers

from .models import CatalogItem


class CatalogItemSerializer(serializers.ModelSerializer):
    # на запись принимаем файл, на чтение отдаем относительный url —
    # чтобы при SSR в него не подставился внутренний хост backend:8000
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CatalogItem
        fields = ("id", "name", "description", "image", "image_url", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None
