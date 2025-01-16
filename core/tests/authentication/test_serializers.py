import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from apps.authentication.serializers import CustomUserSerializer

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserSerializer:

    def test_serializer_fields(self):
        # Check that serializer has the correct fields
        serializer = CustomUserSerializer()
        assert set(serializer.fields.keys()) == {
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "is_active",
            "is_staff",
        }

    def test_passwords_must_match(self):
        # Test that the serializer raises an error if passwords do not match
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "Yusof12345",
            "password2": "differentpassword",
            "is_active": True,
            "is_staff": False,
        }
        serializer = CustomUserSerializer(data=data)
        with pytest.raises(ValidationError, match="Passwords do not match"):
            serializer.is_valid(raise_exception=True)

    def test_create_user_with_valid_data(self):
        # Test user creation with valid data
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "Yusof12345",
            "password2": "Yusof12345",
            "is_active": True,
            "is_staff": False,
        }
        serializer = CustomUserSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Validate the created user
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.check_password("Yusof12345")  # Check that password is hashed

    def test_update_user_with_new_password(self):
        # Test updating a user with a new password
        user = User.objects.create_user(
            email="user@example.com", password="oldpassword"
        )
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "password": "newYusof12345",
            "password2": "newYusof12345",
        }
        serializer = CustomUserSerializer(instance=user, data=data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()

        # Check that the password is updated and other fields are modified correctly
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "User"
        assert updated_user.check_password(
            "newYusof12345"
        )  # Password updated and hashed

    def test_get_tokens(self):
        # Test the get_tokens method for JWT generation
        user = User.objects.create_user(email="user@example.com", password="Yusof12345")
        serializer = CustomUserSerializer()
        tokens = serializer.get_tokens(user)

        # Verify that tokens contain both access and refresh tokens
        assert "refresh" in tokens
        assert "access" in tokens
