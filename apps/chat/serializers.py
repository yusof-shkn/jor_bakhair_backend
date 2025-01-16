from rest_framework import serializers
from .models import Interest, Messages
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "profile_picture",
        ]


class InterestSerializer(serializers.ModelSerializer):
    sender = SimpleUserSerializer()
    receiver = SimpleUserSerializer()

    class Meta:
        model = Interest
        fields = ["sender", "receiver", "status"]

    def validate(self, data):
        if data["sender"] == data["receiver"]:
            raise serializers.ValidationError("You cannot send interest to yourself.")
        return data


class UserDataSerializerSent(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "status",
        ]

    def get_status(self, obj):
        request = self.context.get("request")
        if not request:
            return None  # Return None if no request context is provided

        sender = request.user
        print(sender)
        receiver = obj  # The user object being serialized

        # Retrieve the single interest between sender and receiver
        try:
            interest = Interest.objects.get(sender=sender, receiver=receiver)
            print(interest.sender, interest.receiver)
            return interest.status  # Return the status field
        except Interest.DoesNotExist:
            return None  # Return None if no interest exists


class UserDataSerializerReceived(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "status",
        ]

    def get_status(self, obj):
        request = self.context.get("request")
        if not request:
            return None  # Return None if no request context is provided

        # Retrieve the interest where the current user is the receiver and obj is the sender
        try:
            interest = Interest.objects.get(sender=obj, receiver=request.user)
            return interest.status  # Return the status field
        except Interest.DoesNotExist:
            return None  # Return None if no interest exists


class InterestAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["id", "sender", "receiver", "status", "created_at"]

    def validate(self, data):
        if data["sender"] == data["receiver"]:
            raise serializers.ValidationError("You cannot send interest to yourself.")
        return data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ["id", "sender", "receiver", "message", "is_read"]


class LastMessageSerializer(serializers.ModelSerializer):
    # sender = SimpleUserSerializer()
    # receiver = SimpleUserSerializer()

    class Meta:
        model = Messages
        fields = ["message", "date"]
