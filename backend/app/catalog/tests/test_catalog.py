from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from catalog.models import CatalogItem

User = get_user_model()


def png():
    # маленькая валидная картинка для загрузки
    buf = BytesIO()
    Image.new("RGB", (4, 4), "red").save(buf, "PNG")
    return SimpleUploadedFile("x.png", buf.getvalue(), content_type="image/png")


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
    for i in range(15):
        CatalogItem.objects.create(name=f"item {i}")
    r = client.get("/api/catalog/")
    assert r.status_code == 200
    assert r.data["count"] == 15
    assert len(r.data["results"]) == 12  # PAGE_SIZE
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
