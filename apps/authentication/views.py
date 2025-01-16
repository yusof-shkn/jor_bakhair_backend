from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, AccessTokenSerializer, LoginSerializer
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from dotenv import load_dotenv
from rest_framework_simplejwt.exceptions import TokenError
import os
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()
load_dotenv()
FRONTEND_DOMAIN = os.environ.get("FRONTEND_DOMAIN")


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request):
        """
        Handle POST request for user registration.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Save the user and get the instance
            user = serializer.save()

            # Update the last login field
            update_last_login(None, user)

            # Get JWT tokens for the registered user
            tokens = serializer.get_tokens(user)

            # Return the user data and tokens
            return Response(
                {
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                    "tokens": tokens,
                },
                status=status.HTTP_201_CREATED,
            )
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    Handle POST request for user login.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Update the last login field
            update_last_login(None, user)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Set the refresh token as an HTTP-only cookie

            response = Response(
                {
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "profile_picture": user.profile_picture.url or None,
                    },
                    "access_token": access_token,  # Include the access token in the response
                    "refresh_token": "Set in the Cookie",
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,  # Ensures the cookie is not accessible via JavaScript
                secure=True,  # Use True if your application is served over HTTPS
                samesite="None",  # Adjust based on your needs: 'Strict', 'Lax', or 'None'
                max_age=7 * 24 * 60 * 60,  # Set the cookie to expire in 7 days
            )

            return response

        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutAPIView(APIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalidate the token
            return Response(
                {"message": "logout successfully"}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            print("error", e)

            return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).first()
        print(user)
        if user:
            token = PasswordResetTokenGenerator().make_token(user)
            # Generate a password reset link with token (e.g., frontend link)
            reset_link = f"{FRONTEND_DOMAIN}/reset-password/{token}"
            send_mail(
                "Password Reset Request",
                f"Use this link to reset your password: {reset_link}",
                "admin@yourapp.com",
                [email],
                fail_silently=False,
            )
            return Response(
                {"detail": "Password reset email sent"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "User with this email not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetConfirmAPIView(APIView):
    serializer_class = CustomUserSerializer

    def post(self, request, token):
        password = request.data.get("password")
        user = CustomUser.objects.filter(email=request.data.get("email")).first()

        if user and PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(password)
            user.save()
            return Response(
                {"detail": "Password successfully reset"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid token or user"}, status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password successfully changed"}, status=status.HTTP_200_OK
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user

        # Extracting data and files
        data = request.data.dict()  # Convert QueryDict to a standard dictionary
        files = request.FILES

        # Merge form data and file data
        if "profile_picture" in files:
            data["profile_picture"] = files["profile_picture"]

        # Extract password
        password = data.get("password")
        if not password:
            return Response(
                {"password": "Password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate the user
        authenticated_user = authenticate(username=user.email, password=password)
        if not authenticated_user:
            return Response(
                {"password": "Invalid password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Pass the data to the serializer
        serializer = self.serializer_class(user, data=data, partial=True)
        if not serializer.is_valid():
            print(f"Validation Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get(self, request):
        user_id = request.GET.get("user_id")
        if not user_id:
            return Response(
                {"error": "user_id query parameter is required."}, status=400
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses=AccessTokenSerializer  # Reference the serializer class here
    )
    def get(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            active_token = RefreshToken(refresh_token)
        except TokenError as e:
            response = Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            response.delete_cookie("refresh_token")
            return response
        data = {
            "access_token": str(active_token.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)
