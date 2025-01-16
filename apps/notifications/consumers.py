from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    import json

    async def connect(self):
        from django.core.cache import cache
        from django.contrib.auth.models import AnonymousUser

        # Extract the token from the query string
        query_string = self.scope["query_string"].decode()
        token = self._extract_token_from_query_string(query_string)

        # Authenticate the user
        self.scope["user"] = await self._get_user_from_token(token)

        # If the user is not authenticated, close the connection
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        self.group_name = f"notifications_{self.scope['user'].id}"

        # Cache key to track active user connections
        cache_key = f"active_connection_{self.scope['user'].id}_"

        # Check if the user is already connected by checking the cache
        if cache.get(cache_key):
            # If the user is already connected, reject the new connection
            await self.close()
            return

        # Mark the user as connected by setting the cache
        cache.set(
            cache_key, self.channel_name, timeout=2
        )  # Set the timeout to 1 hour (or your preference)

        # Add this connection to the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        print(f"WebSocket connected for user: {self.scope['user']}")

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        """
        print(f"Received data: {text_data}")
        pass

    async def send_notification(self, event):
        """
        Send a new notification to the WebSocket.
        """
        notification_id = event["notification_id"]
        notification_type = event["notification_type"]
        print(notification_type)
        await self.send(
            text_data=self.json.dumps(
                {
                    "type": notification_type,
                    "notification_id": notification_id,
                }
            )
        )

    def _extract_token_from_query_string(self, query_string):
        """
        Extract the token from the query string.
        """
        params = dict(param.split("=") for param in query_string.split("&"))
        return params.get("token")

    async def _get_user_from_token(self, token):
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import AnonymousUser

        User = get_user_model()
        """
        Decode the JWT token and fetch the user.
        """
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = await User.objects.filter(id=user_id).afirst()
            return user or AnonymousUser()
        except Exception:
            return AnonymousUser()
