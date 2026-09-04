from rest_framework import serializers

from .models import CatalogItem


class CatalogItemSerializer(serializers.ModelSerializer):
    # на запись принимаем файл, на чтение отдаем относительный url —
    # чтобы при SSR в него не подставился внутренний хост backend:8000
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    # флаг явной очистки картинки (multipart не умеет слать null)
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = CatalogItem
        fields = ("id", "name", "description", "image", "image_url", "remove_image", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    def create(self, validated_data):
        validated_data.pop("remove_image", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove = validated_data.pop("remove_image", False)
        # старый файл убираем с диска при замене или очистке
        if (remove or validated_data.get("image")) and instance.image:
            instance.image.delete(save=False)
        if remove:
            validated_data["image"] = None
        return super().update(instance, validated_data)
