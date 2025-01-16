from django.contrib.auth import get_user_model
import requests
from .models import Notification
from channels.layers import get_channel_layer

# URL of the DRF view that sends notifications to WebSocket
NOTIFICATION_API_URL = "http://192.168.150.14:4000/api/notifications/send-notification/"

User = get_user_model()


def send_notification(user_id: int, message: str, notification_type: int):
    """
    Creates a notification for a user and sends it to the WebSocket server via a POST request.
    It also generates an access token for the user.

    Args:
        user_id: The ID of the user to receive the notification.
        message: The message content of the notification.
        notification_type: Type of the notification (INFO, WARN, etc.).
    """
    try:

        # Prepare the data to send in the POST request
        notification = Notification.objects.create(
            recipient_id=user_id,
            message=message,
            type=notification_type,
            is_read=False,
        )
        channel_layer = get_channel_layer()
        group_name = f"notifications_{user_id}"

        from asgiref.sync import async_to_sync

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification_type": notification.type,
                "notification_id": notification.id,
            },
        )

    except User.DoesNotExist:
        print(f"Error: User with ID {user_id} not found.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {e}")
