import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationViews:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def create_user(self):
        return User.objects.create_user(email="user@example.com", password="Yusof12345")

    def test_register(self, api_client):
        url = reverse("register")
        data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "Yusof12345",
            "password2": "Yusof12345",
        }
        response = api_client.post(url, data)
        print(response)
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data

    def test_login(self, api_client, create_user):
        url = reverse("login")
        data = {"email": "user@example.com", "password": "Yusof12345"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data

    def test_logout(self, api_client, create_user):
        # Get refresh token for the user
        user = create_user
        refresh = RefreshToken.for_user(user)

        url = reverse("logout")
        data = {"refresh": str(refresh)}
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_password_reset_request(self, api_client, create_user, mocker):
        mocker.patch(
            "django.core.mail.send_mail", return_value=1
        )  # Mock the send_mail function
        url = reverse("password_reset_request")
        data = {"email": "user@example.com"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Password reset email sent"

    def test_password_reset_confirm(self, api_client, create_user, mocker):
        user = create_user
        token = PasswordResetTokenGenerator().make_token(user)

        url = reverse("password_reset_confirm", args=[token])
        data = {"email": "user@example.com", "password": "newYusof12345"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("newYusof12345")

    def test_change_password(self, api_client, create_user):
        user = create_user
        api_client.force_authenticate(user=user)
        url = reverse("change_password")
        data = {
            "old_password": "Yusof12345",
            "new_password": "newYusof12345",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("newYusof12345")

    def test_profile_view_get(self, api_client, create_user):
        user = create_user
        api_client.force_authenticate(user=user)
        url = reverse("profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "user@example.com"

    def test_profile_view_update(self, api_client, create_user):
        user = create_user
        api_client.force_authenticate(user=user)
        url = reverse("profile")
        data = {
            "first_name": "Updated",
            "password": "Yusof12345",
            "password2": "Yusof12345",
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
