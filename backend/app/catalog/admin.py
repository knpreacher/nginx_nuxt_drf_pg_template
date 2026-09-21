from django.contrib import admin

from .models import CatalogItem


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ("name", "is_public", "created_at", "updated_at")
    list_editable = ("is_public",)
    search_fields = ("name", "description")
