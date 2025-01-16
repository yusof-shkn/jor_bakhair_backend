from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Retrieve a list of notifications or a single notification.
        """
        if pk:
            # If pk is provided, return a single notification
            notification = get_object_or_404(
                Notification, pk=pk, recipient=request.user
            )
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        else:
            # Otherwise, return a list of notifications
            is_read = request.data.get("is_read", None)
            if is_read is not None:
                count_is_read = Notification.objects.filter(
                    recipient=request.user, is_read=is_read.lower() == "true"
                ).count()
                return Response(count_is_read)
            else:
                notifications = Notification.objects.filter(recipient=request.user)
                serializer = NotificationSerializer(notifications, many=True)
                return Response(serializer.data)

    def post(self, request):
        """
        Create a new notification.
        """
        recipient_id = request.data.get("recipient")
        message = request.data.get("message")
        notification_type = request.data.get(
            "notification_type", 1
        )  # Default to 1 if not provided

        if not recipient_id or not message:
            return Response(
                {"error": "Recipient and message are required."}, status=400
            )

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({"error": "Recipient not found."}, status=404)

        # Create the notification
        notification = Notification.objects.create(
            recipient=recipient,
            message=message,
            notification_type=notification_type,
        )

        # Serialize and return the newly created notification
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=201)

    def put(self, request):
        """
        Update multiple notifications (Mark as Read/Unread).
        """
        notification_ids = request.data.get("notification_ids", [])
        mark_as_read = request.data.get("mark_as_read", None)

        if not notification_ids:
            return Response(
                {"error": "No notification IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mark_as_read is None:
            return Response(
                {"error": "You must specify whether to mark as read or unread."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure that mark_as_read is a boolean value
        if not isinstance(mark_as_read, bool):
            return Response(
                {"error": "mark_as_read must be a boolean value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch notifications that belong to the authenticated user and are in the provided IDs
        notifications = Notification.objects.filter(
            pk__in=notification_ids, recipient=request.user
        )

        # Update the 'is_read' field for the selected notifications
        updated_count = notifications.update(is_read=mark_as_read)

        if updated_count == 0:
            return Response(
                {"error": "No matching notifications found to update."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "detail": f"{updated_count} notification(s) marked as {'read' if mark_as_read else 'unread'}."
            }
        )

    def delete(self, request, pk):
        """
        Delete a notification.
        """
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.delete()
            return Response({"detail": "Notification deleted."})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found."}, status=404)


class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Retrieve a list of notifications or a single notification.
        """
        notifications_count = Notification.objects.filter(
            recipient=request.user, type=pk
        ).count()
        return Response(notifications_count)
