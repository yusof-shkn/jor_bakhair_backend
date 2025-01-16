from django.db import models
from django.contrib.auth import get_user_model


class Interest(models.Model):
    sender = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="sent_interests"
    )
    receiver = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="received_interests"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("blocked", "Blocked"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"], name="unique_interest_per_pair"
            )
        ]

    def __str__(self):
        return f"Interest from {self.sender} to {self.receiver} - {self.status}"


class Messages(models.Model):
    sender = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="sent_message"
    )
    receiver = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="received_message"
    )
    message = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        """Mark the notification as unread."""
        self.is_read = False
        self.save()

    class Meta:
        ordering = ["date"]
        # verbos_plural_name = "Message"

    def __str__(self):
        return f"{self.sender} - {self.receiver}"
