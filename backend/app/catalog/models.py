from django.db import models


class CatalogItem(models.Model):
    name = models.CharField("название", max_length=255)
    description = models.TextField("описание", blank=True)
    image = models.ImageField("картинка", upload_to="catalog/", blank=True, null=True)
    # виден на публичном лендинге без авторизации
    is_public = models.BooleanField("публичный", default=False)
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("изменен", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "элемент каталога"
        verbose_name_plural = "каталог"

    def __str__(self):
        return self.name
