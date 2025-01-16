from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.notifications.utils import send_notification


def notify_via_websocket(user_id, message_id):
    """
    Send a notification to a WebSocket room with the message ID.
    """
    # Send notification to WebSocket room
    send_notification(user_id, message_id, 2)
    group_name = f"messages_{user_id}"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "notify_new_message",
            "message_id": message_id,
        },
    )
