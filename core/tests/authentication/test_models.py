import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserManager:

    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        assert user.email == "test@example.com"
        assert user.check_password("password123") is True
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_without_email(self):
        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email=None, password="password123")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        assert superuser.email == "admin@example.com"
        assert superuser.check_password("password123") is True
        assert superuser.is_active
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_create_superuser_without_is_staff(self):
        with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
            User.objects.create_superuser(
                email="admin@example.com", password="password123", is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
            User.objects.create_superuser(
                email="admin@example.com", password="password123", is_superuser=False
            )


@pytest.mark.django_db
class TestCustomUserModel:

    def test_user_string_representation(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        assert str(user) == "testuser@example.com"
