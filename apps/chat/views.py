from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework import generics, permissions
from .serializers import (
    UserDataSerializerSent,
    UserDataSerializerReceived,
    InterestSerializer,
    MessageSerializer,
    InterestAddSerializer,
    SimpleUserSerializer,
    LastMessageSerializer,
)
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Interest, Messages
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from apps.notifications.utils import send_notification
from django.shortcuts import get_object_or_404
from .models import Messages
from .utils import notify_via_websocket

User = get_user_model()


@api_view(["GET"])
def index(request):
    return Response("API's Floating")


class Home(APIView):
    def get(self, request):
        content = {"message": "Hello, World!"}
        return Response(content)


class SearchUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.GET.get("query", None)

        # Filter users based on the search query
        if search_query:
            users = User.objects.filter(
                Q(email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            ).exclude(id=request.user.id)
        else:
            users = User.objects.none()  # Empty queryset if no query provided

        # Serialize the user data with interests
        serializer = UserDataSerializerSent(
            users, many=True, context={"request": request}
        )

        # Return serialized data
        return Response(serializer.data, status=200)


# 4. send interest
class InterestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        interests = Interest.objects.filter(
            receiver=request.user, status__in=["pending", "accepted"]
        ).select_related("sender")

        if not interests.exists():
            raise NotFound("No pending or accepted interests found.")

        # Extract the sender users from the interests
        senders = [interest.sender for interest in interests]

        # Serialize the senders using UserDataSerializerReceived
        serializer = UserDataSerializerReceived(
            senders, many=True, context={"request": request}
        )
        return Response(serializer.data, status=200)

    def post(self, request):
        receiver_id = request.data.get("receiver")

        # Ensure receiver exists
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Validate that the sender is not the same as the receiver
        if request.user.id == receiver.id:
            return Response(
                {"detail": "You cannot send interest to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interest_data = {
            "sender": request.user.id,
            "receiver": receiver.id,
            "status": "pending",
        }

        print("Interest data?", interest_data)
        existing_interest = Interest.objects.filter(
            sender=request.user.id, receiver=receiver.id, status="pending"
        ).first()

        if existing_interest:
            # Serialize existing interest data and return it
            if (
                existing_interest.status == "pending"
                or existing_interest.status == "Pending"
            ):
                existing_interest.delete()
                return Response({"status": None}, status=status.HTTP_200_OK)
            else:
                serializer = InterestAddSerializer(existing_interest)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # If no existing interest, create a new one
        serializer = InterestAddSerializer(data=interest_data)
        if serializer.is_valid():
            serializer.save()

            # Create a notification for the receiver
            send_notification(
                receiver.id,
                f"You have a new interest from {request.user.first_name}.",
                1,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 6. accept interest
class ActionInterestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch interests with accepted status for the authenticated user
            interests = Interest.objects.filter(
                Q(sender=self.request.user, status="accepted")
                | Q(receiver=self.request.user, status="accepted")
            ).select_related(
                "sender", "receiver"
            )  # Optimize queries

            # Extract the relevant user data (either sender or receiver)
            users = []
            for interest in interests:
                if interest.sender == self.request.user:
                    users.append(interest.receiver)

            # Serialize the user data
            serializer = SimpleUserSerializer(users, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        sender_id = request.data.get("receiver_id", None)
        user = request.user
        user_ = User.objects.get(id=sender_id)
        try:
            interest = Interest.objects.get(
                sender=sender_id, receiver=request.user, status="pending"
            )
        except Interest.DoesNotExist:
            return Response(
                {"detail": "Interest not found or not authorized."},
                status=status.HTTP_404_NOT_FOUND,
            )
        action = request.data.get("action", None)
        if action == "accept":
            Interest.objects.create(sender=user, receiver=user_, status="accepted")
            interest.status = "accepted"
            interest.save()
            send_notification(
                user_.id,
                f"{(user.first_name).capitalize()} accepted your Interest request.",
                1,
            )
            return Response({"detail": "Interest accepted."})
        else:
            interest.delete()
            return Response({"detail": "Interest rejected."})

    def delete(self, request):
        # Get the user_id from query parameters
        user_id = request.GET.get("user_id", None)
        if not user_id:
            return Response(
                {"detail": "User ID is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the logged-in user
        user = request.user

        # Fetch the interests involving the logged-in user and the specified user
        interests = Interest.objects.filter(
            Q(sender=user, receiver_id=user_id, status="accepted")
            | Q(sender_id=user_id, receiver=user, status="accepted")
        )

        if not interests.exists():
            return Response(
                {"detail": "No interests found for the specified user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete associated messages
        messages = Messages.objects.filter(
            Q(sender=user, receiver_id=user_id) | Q(sender_id=user_id, receiver=user)
        )
        deleted_messages_count = messages.delete()[
            0
        ]  # delete() returns a tuple (count, _)

        # Delete the interests
        deleted_interests_count = interests.delete()[0]

        return Response(
            {
                "detail": f"{deleted_interests_count} interest(s) and {deleted_messages_count} message(s) deleted successfully."
            },
            status=status.HTTP_200_OK,
        )


class MessagesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        """
        Retrieve a specific message by ID or all messages between the authenticated user and a specified receiver.
        """
        if id:
            # Retrieve a single message
            queryset = Messages.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user)
            )
            message = get_object_or_404(queryset, id=id)
            serializer = MessageSerializer(message)
            serializer.update(is_read=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        receiver_id = request.query_params.get("user_id")
        if not receiver_id:
            return Response(
                {"detail": "Receiver ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND
            )

        messages = Messages.objects.filter(
            Q(sender=request.user, receiver=receiver)
            | Q(sender=receiver, receiver=request.user)
        )
        serializer = MessageSerializer(messages, many=True)
        import json

        print(json.dumps(serializer.data, indent=4))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new message from the authenticated user to a specified receiver.
        """
        print("Request data:", request.data)
        receiver_id = request.data.get("receiver_id")

        if not receiver_id:
            return Response(
                {"detail": "Receiver ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Prepare data for the serializer
        data = request.data.copy()
        data.pop("receiver_id", None)
        data["receiver"] = receiver.id
        data["sender"] = request.user.id

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            message_id = serializer.save().id
            notify_via_websocket(receiver_id, message_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """
        Update a message by ID.
        Only the sender of the message is allowed to update it.
        """
        message = get_object_or_404(Messages, id=id, sender=request.user)
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """
        Mark all messages as read between the authenticated user and a specified receiver.
        """
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "Receiver ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_ = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Mark all unread messages as read
        Messages.objects.filter(
            Q(sender=user_, receiver=request.user),
            is_read=False,
        ).update(is_read=True)

        return Response(
            {"detail": "All messages marked as read."},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        """
        Delete a message by ID.
        Only the sender of the message is allowed to delete it.
        """
        message = get_object_or_404(Messages, id=id, sender=request.user)
        message.delete()
        return Response(
            {"detail": "Message deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class MessageView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, message_id):
        user = request.user

        # Retrieve the message or return a 404 response if not found
        message = get_object_or_404(Messages, receiver=user, id=message_id)

        # Serialize the message object
        serializer = self.serializer_class(message)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


class AcceptedInterestWithMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all accepted interests where the logged-in user is either the sender or receiver
        accepted_interests = Interest.objects.filter(
            Q(sender=user) | Q(receiver=user), status="accepted"
        )

        # Get the IDs of users with whom the logged-in user has an accepted interest
        interest_partner_ids = set(
            accepted_interests.values_list("sender_id", "receiver_id", flat=False)
        )

        # Find messages exchanged between the logged-in user and their interest partners
        messages = Messages.objects.filter(
            Q(sender=user, receiver__in=interest_partner_ids)
            | Q(receiver=user, sender__in=interest_partner_ids)
        ).order_by(
            "-date"
        )  # Order by the latest message first

        # Select only the latest message for each unique sender-receiver pair
        unique_messages = {}
        unread_counts = {}

        for message in messages:
            key = frozenset([message.sender_id, message.receiver_id])

            if key not in unique_messages:
                unique_messages[key] = message

            # Count unread messages where the receiver is the logged-in user
            if message.receiver == user and not message.is_read:
                # Count only messages the other user sent to the authenticated user
                unread_counts[message.sender_id] = (
                    unread_counts.get(message.sender_id, 0) + 1
                )

        # Prepare serialized response
        serialized_data = []
        for message in unique_messages.values():
            # Get the user that is the "partner" (not the current user)
            partner = message.sender if message.sender != user else message.receiver
            partner_data = SimpleUserSerializer(partner).data

            # Prepare the last message data
            last_message_data = LastMessageSerializer(message).data

            # Add unread message count for the partner
            unread_count = unread_counts.get(partner.id, 0)

            # Add the full response object for this partner
            serialized_data.append(
                {
                    "user": partner_data,
                    "last_message": last_message_data,
                    "unread_count": unread_count,  # Include unread message count
                }
            )
        import json

        print("Serialized data", json.dumps(serialized_data, indent=4))
        return Response(serialized_data)
