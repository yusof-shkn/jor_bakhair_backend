from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import ImageField


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "profile_picture",
            "is_active",
            "is_staff",
        )

    @extend_schema_field(ImageField)
    def profile_picture(self):
        return self.profile_picture

    def validate(self, data):
        """
        Ensure the two password fields match.
        """
        validate_password(data["password"])
        return data

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        """
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing user instance, given the validated data.
        """
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(
                password
            )  # If password is updated, hash the new password

        instance.save()
        return instance

    def get_tokens(self, user):
        """
        Generate JWT tokens for the user
        """
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
