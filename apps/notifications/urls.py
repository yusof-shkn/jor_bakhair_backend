from django.urls import path
from .views import NotificationView, NotificationCountView

urlpatterns = [
    path("", NotificationView.as_view()),
    path("<int:pk>/", NotificationView.as_view()),
    path("count/<int:pk>/", NotificationCountView.as_view()),
]
