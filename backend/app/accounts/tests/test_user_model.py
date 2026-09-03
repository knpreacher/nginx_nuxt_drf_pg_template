import uuid
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user_with_email_no_username():
    u = User.objects.create_user(email="a@b.com", password="pw12345!")
    assert isinstance(u.id, uuid.UUID)
    assert u.email == "a@b.com"
    assert u.check_password("pw12345!")
    assert u.username is None  # поле убрано
    assert User.USERNAME_FIELD == "email"


@pytest.mark.django_db
def test_create_superuser():
    su = User.objects.create_superuser(email="admin@b.com", password="pw12345!")
    assert su.is_staff and su.is_superuser


@pytest.mark.django_db
def test_email_is_unique():
    User.objects.create_user(email="a@b.com", password="pw")
    with pytest.raises(Exception):
        User.objects.create_user(email="a@b.com", password="pw")
