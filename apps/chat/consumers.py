# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# import json
# from django.contrib.auth import get_user_model
# from django.db.models import Q
# from urllib.parse import parse_qs


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         from rest_framework.exceptions import AuthenticationFailed
#         from rest_framework_simplejwt.tokens import AccessToken

#         self.room_name = "Chat"
#         self.room_group_name = "ChatGroup"
#         print("Incoming connection:", self.scope)

#         # Parse query string for token and recipient ID
#         query_string = self.scope["query_string"].decode()
#         query_params = parse_qs(query_string)
#         token = query_params.get("token", [None])[0]
#         print("first part ", token)
#         recipient_id = query_params.get("receipent", [None])[0]
#         if not token:
#             await self.close(code=4001)  # Custom close code for "missing token"
#             return

#         try:
#             # Decode the token using DRF SimpleJWT's AccessToken
#             access_token = AccessToken(token)
#             user_id = access_token["user_id"]
#         except Exception as e:
#             # Handle invalid or expired tokens
#             print(f"Token error: {str(e)}")
#             await self.close(code=4002)  # Custom close code for "invalid token"
#             return

#         # Generate room name based on both user IDs
#         self.room_group_name = self.get_room_name(user_id, recipient_id)

#         # Add the user to the room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         # Accept the WebSocket connection
#         await self.accept()

#         # Send confirmation to the client
#         await self.send(
#             text_data=json.dumps(
#                 {"type": "websocket_connected", "room": self.room_group_name}
#             )
#         )

#     def get_room_name(self, user_id, recipient_id):
#         """Generate a unique room name for the two users"""
#         if user_id and recipient_id:
#             return f"chat_{min(user_id, recipient_id)}_{max(user_id, recipient_id)}"
#         return self.room_group_name

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         import jwt
#         from rest_framework.exceptions import AuthenticationFailed
#         from rest_framework_simplejwt.tokens import AccessToken

#         # User = self.get_user()
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         receiver_id = text_data_json["receiver"]
#         token = text_data_json["sender"]

#         # Authenticate sender using token
#         try:
#             payload = AccessToken(token)
#             sender_id = payload["user_id"]
#         except jwt.ExpiredSignatureError:
#             raise AuthenticationFailed("access_token expired")
#         except jwt.InvalidTokenError:
#             raise AuthenticationFailed("Invalid token")

#         # Save the message to the database
#         message_id = await self.save_message(sender_id, receiver_id, message)

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "message_id": message_id,
#             },
#         )

#     async def chat_message(self, event):
#         message_id = event["message_id"]  # Ensure receiver is handled as well

#         # Send message to WebSocket, including both sender and receiver
#         await self.send(
#             text_data=json.dumps(
#                 {
#                     "message_id": message_id,
#                 }
#             )
#         )

#     @database_sync_to_async
#     def save_message(self, sender_id, receiver_id, message):
#         from .models import Messages
#         from apps.notifications.utils import send_notification

#         User = get_user_model()

#         sender = User.objects.get(id=sender_id)
#         receiver = User.objects.get(id=receiver_id)
#         saved_message = Messages.objects.create(
#             sender=sender, receiver=receiver, message=message
#         )

#         new_message = {"sender": (sender.first_name).capitalize(), "message": message}
#         send_notification(
#             receiver.id,
#             str(new_message),
#             "Message",
#         )
#         return saved_message.id

#     def get_room_name(self, user1_id, user2_id):
#         # Ensure both IDs are integers
#         user1_id = int(user1_id)
#         user2_id = int(user2_id)
#         # Generate a unique room name based on sorted user IDs
#         return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"


from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs


class ChatConsumer(AsyncWebsocketConsumer):

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

        self.group_name = f"messages_{self.scope['user'].id}"

        # Cache key to track active user connections
        cache_key = f"active_connection_messages_{self.scope['user'].id}_"

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

    async def notify_new_message(self, event):
        message_id = event["message_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "message_id": message_id,
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
