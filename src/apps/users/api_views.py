"""API views for OTP authentication flow. Handles HTTP layer only. Business logic is delegated to services module."""
import time

from django.contrib.auth import get_user_model
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwner
from .serializers import (ActivateInviteSerializer, ProfileSerializer,
                          RequestCodeSerializer, VerifyCodeSerializer)
from .services import activate_invite, request_otp, verify_otp


@extend_schema(
    tags=["Auth"],
    summary="Request OTP code",
    description="Generates and sends OTP code to provided phone number.",
    request=RequestCodeSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Phone example",
            value={"phone": "+79991234567"},
            request_only=True,
        ),
        OpenApiExample(
            "Success response",
            value={"detail": "OTP sent"},
            response_only=True,
        ),
    ],
)
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


@extend_schema(
    tags=["Auth"],
    summary="Verify OTP code",
    description="Verifies phone number and OTP code to provide access and refresh tokens.",
    request=VerifyCodeSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Phone and code example",
            value={"phone": "+79991234567", "code": "123456"},
            request_only=True,
        ),
        OpenApiExample(
            "JWT response",
            value={
                "access": "eyJhbGciOiJIUzI1NiI...",
                "refresh": "eyJhbGciOiJIUzI1Ni..."
            },
            response_only=True,
        ),
    ],
)
class VerifyCodeView(APIView):
    """ POST endpoint to verify OTP code.
        Flow:
            1. Validate input.
            2. Verify OTP via service layer.
            3. Return JWT tokens if successful."""

    def get(self, request):
        phone = request.GET.get("phone")
        return render(request, "users/verify.html", {"phone": phone})

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = verify_otp(
            serializer.validated_data["phone"],
            serializer.validated_data["code"]
        )

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(tags=["Profile"])
class ProfileView(APIView):
    """GET endpoint for retrieving current user's profile."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="profile_current",
        summary="Get current user profile",
        description="Returns authenticated user's profile.",
        responses={200: ProfileSerializer},
        examples=[
            OpenApiExample(
                "Phone example",
                value={"phone": "+79991234567"},
                request_only=True,
            ),
            OpenApiExample(
                "Success response",
                value={
                    "phone": "+79991234567",
                    "invite_code": "Z0R13P",
                    "invited_by": "",
                    "referrals": []
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["Referral"],
    summary="Activate invite code",
    description="Assign inviter and update referral list.",
    request=ActivateInviteSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Invite_code example",
            value={"invite_code": "OBENAJ"},
            request_only=True,
        ),
        OpenApiExample(
            "Success response",
            value={"detail": "Invite activated"},
            response_only=True,
        ),
    ],
)
class ActivateInviteView(APIView):
    """POST endpoint for activating referral invite code."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ActivateInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activate_invite(request.user, serializer.validated_data["invite_code"],)

        return Response({"detail": "Invite activated"}, status=status.HTTP_200_OK,)


User = get_user_model()


@extend_schema(tags=["Profile"])
class OwnerProfileView(RetrieveAPIView):
    """Retrieve user profile by ID with owner-only access."""
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_url_kwarg = "user_id"

    @extend_schema(
        operation_id="profile_retrieve_by_id",
        summary="Retrieve profile by ID",
        description="Returns profile only if requesting user is the owner.",
        responses={
            200: ProfileSerializer,
            403: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Phone example",
                value={"phone": "+79991234567"},
                request_only=True,
            ),
            OpenApiExample(
                "Success response",
                value={
                    "phone": "+79991234567",
                    "invite_code": "Z0R13P",
                    "invited_by": "",
                    "referrals": []
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
