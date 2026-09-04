from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from catalog.models import CatalogItem

User = get_user_model()


def png(name="x.png"):
    # маленькая валидная картинка для загрузки
    buf = BytesIO()
    Image.new("RGB", (4, 4), "red").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@pytest.fixture
def client(db):
    user = User.objects.create_user(email="a@b.com", password="pw12345!")
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


@pytest.mark.django_db
def test_list_requires_auth():
    assert APIClient().get("/api/catalog/").status_code == 401


@pytest.mark.django_db
def test_list_paginated(client):
    from rest_framework.settings import api_settings

    size = api_settings.PAGE_SIZE
    n = size + 3
    for i in range(n):
        CatalogItem.objects.create(name=f"item {i}")
    r = client.get("/api/catalog/")
    assert r.status_code == 200
    assert r.data["count"] == n
    assert len(r.data["results"]) == size  # первая страница заполнена целиком
    assert r.data["next"]


@pytest.mark.django_db
def test_search(client):
    CatalogItem.objects.create(name="красный стул", description="дерево")
    CatalogItem.objects.create(name="синий стол", description="металл")
    r = client.get("/api/catalog/", {"search": "стул"})
    assert r.data["count"] == 1
    assert r.data["results"][0]["name"] == "красный стул"


@pytest.mark.django_db
def test_search_by_description(client):
    CatalogItem.objects.create(name="одно", description="уникальное слово")
    CatalogItem.objects.create(name="два", description="другое")
    r = client.get("/api/catalog/", {"search": "уникальное"})
    assert r.data["count"] == 1


@pytest.mark.django_db
def test_ordering_by_name(client):
    CatalogItem.objects.create(name="бета")
    CatalogItem.objects.create(name="альфа")
    r = client.get("/api/catalog/", {"ordering": "name"})
    names = [x["name"] for x in r.data["results"]]
    assert names == ["альфа", "бета"]


@pytest.mark.django_db
def test_create_with_image(client, media):
    r = client.post(
        "/api/catalog/",
        {"name": "новый", "description": "тест", "image": png()},
        format="multipart",
    )
    assert r.status_code == 201, r.data
    assert r.data["name"] == "новый"
    assert r.data["image_url"] and r.data["image_url"].startswith("/media/")
    assert r.data["created_at"] and r.data["updated_at"]


@pytest.mark.django_db
def test_create_without_image(client):
    r = client.post("/api/catalog/", {"name": "без картинки"}, format="multipart")
    assert r.status_code == 201, r.data
    assert r.data["image_url"] is None


@pytest.mark.django_db
def test_update(client):
    item = CatalogItem.objects.create(name="старое")
    r = client.patch(f"/api/catalog/{item.id}/", {"name": "новое"}, format="multipart")
    assert r.status_code == 200
    item.refresh_from_db()
    assert item.name == "новое"


@pytest.mark.django_db
def test_delete(client):
    item = CatalogItem.objects.create(name="удалить")
    r = client.delete(f"/api/catalog/{item.id}/")
    assert r.status_code == 204
    assert not CatalogItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db
def test_remove_image_clears_field_and_file(client, media):
    import os

    r = client.post("/api/catalog/", {"name": "с картинкой", "image": png()}, format="multipart")
    item_id = r.data["id"]
    assert r.data["image_url"]
    path = CatalogItem.objects.get(id=item_id).image.path
    assert os.path.exists(path)

    r2 = client.patch(f"/api/catalog/{item_id}/", {"remove_image": "true"}, format="multipart")
    assert r2.status_code == 200
    assert r2.data["image_url"] is None
    assert not CatalogItem.objects.get(id=item_id).image
    assert not os.path.exists(path)  # старый файл удален с диска


@pytest.mark.django_db
def test_replace_image_removes_old_file(client, media):
    import os

    r = client.post("/api/catalog/", {"name": "x", "image": png("a.png")}, format="multipart")
    item_id = r.data["id"]
    old = CatalogItem.objects.get(id=item_id).image.path

    r2 = client.patch(f"/api/catalog/{item_id}/", {"image": png("b.png")}, format="multipart")
    assert r2.status_code == 200
    new = CatalogItem.objects.get(id=item_id).image.path
    assert new != old
    assert os.path.exists(new)
    assert not os.path.exists(old)  # старый файл убран
