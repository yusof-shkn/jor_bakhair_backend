from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    ChangePasswordAPIView,
    UserProfileAPIView,
    ProfileAPIView,
    RefreshTokenView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "password-reset/",
        PasswordResetRequestAPIView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset-confirm/<str:token>/",
        PasswordResetConfirmAPIView.as_view(),
        name="password_reset_confirm",
    ),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("user-profile/", UserProfileAPIView.as_view(), name="profile"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
]
