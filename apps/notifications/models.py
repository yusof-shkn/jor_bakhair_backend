from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        (1, "Type 1"),
        (2, "Type 2"),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.IntegerField(choices=NOTIFICATION_TYPES, default=1)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        """Mark the notification as unread."""
        self.is_read = False
        self.save()

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.notification_type}"
