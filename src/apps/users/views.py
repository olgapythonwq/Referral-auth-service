"""API views for OTP authentication flow. Handles HTTP layer only. Business logic is delegated to services module."""
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsOwner
from .serializers import RequestCodeSerializer, VerifyCodeSerializer, ProfileSerializer, ActivateInviteSerializer
from .services import request_otp, verify_otp, activate_invite
import time


class RequestCodeView(APIView):
    """ POST endpoint to request OTP code.
        Flow:
            1. Validate input.
            2. Create user if not exists.
            3. Generate and save OTP.
            4. Simulate SMS sending delay.
            5. Return success response."""

    def post(self, request):
        serializer = RequestCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_otp(serializer.validated_data["phone"])

        time.sleep(1.5)

        return Response({"detail": "OTP sent"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    """ POST endpoint to verify OTP code.
        Flow:
            1. Validate input.
            2. Verify OTP via service layer.
            3. Return JWT tokens if successful."""


    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = verify_otp(
            serializer.validated_data["phone"],
            serializer.validated_data["code"]
        )

        return Response(tokens, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """GET endpoint for retrieving current user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class ActivateInviteView(APIView):
    """POST endpoint for activating referral invite code."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ActivateInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activate_invite(request.user, serializer.validated_data["invite_code"],)

        return Response({"detail": "Invite activated"}, status=status.HTTP_200_OK,)


User = get_user_model()


class OwnerProfileView(RetrieveAPIView):
    """Retrieve user profile by ID with owner-only access."""
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_url_kwarg = "user_id"
