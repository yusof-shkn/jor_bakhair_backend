from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("search-user/", views.SearchUser.as_view(), name="search_user"),
    # Intersets Endpoints
    path("interest/", views.InterestView.as_view(), name="send-interest"),
    path(
        "interest-action/", views.ActionInterestView.as_view(), name="accept-interest"
    ),
    # chat
    path("messages/", views.MessagesAPIView.as_view(), name="message-list-create"),
    path("messages/<int:id>/", views.MessagesAPIView.as_view(), name="message-detail"),
    path(
        "users-with-messages/",
        views.AcceptedInterestWithMessagesView.as_view(),
        name="users-with-messages",
    ),
]
