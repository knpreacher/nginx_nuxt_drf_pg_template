import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
ACCESS = "access"
REFRESH = "refresh"


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@b.com", password="pw12345!")


@pytest.mark.django_db
def test_login_sets_cookies_and_returns_user(user):
    c = APIClient()
    r = c.post("/api/auth/login/", {"email": "a@b.com", "password": "pw12345!"}, format="json")
    assert r.status_code == 200
    assert r.data["email"] == "a@b.com"
    assert ACCESS in r.cookies and REFRESH in r.cookies
    assert r.cookies[ACCESS]["httponly"]


@pytest.mark.django_db
def test_me_requires_auth():
    assert APIClient().get("/api/auth/me/").status_code == 401


@pytest.mark.django_db
def test_login_then_me(user):
    c = APIClient()
    c.post("/api/auth/login/", {"email": "a@b.com", "password": "pw12345!"}, format="json")
    r = c.get("/api/auth/me/")
    assert r.status_code == 200 and r.data["email"] == "a@b.com"


@pytest.mark.django_db
def test_refresh_issues_new_access(user):
    c = APIClient()
    c.post("/api/auth/login/", {"email": "a@b.com", "password": "pw12345!"}, format="json")
    r = c.post("/api/auth/refresh/")
    assert r.status_code == 200 and ACCESS in r.cookies


@pytest.mark.django_db
def test_logout_clears_cookies(user):
    c = APIClient()
    c.post("/api/auth/login/", {"email": "a@b.com", "password": "pw12345!"}, format="json")
    r = c.post("/api/auth/logout/")
    assert r.status_code == 200
    assert r.cookies[ACCESS].value == "" and r.cookies[REFRESH].value == ""
