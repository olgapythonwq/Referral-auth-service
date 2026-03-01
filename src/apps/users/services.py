"""
Business logic for OTP authentication.
This module contains pure service-layer logic. No HTTP, no serializers, no request objects.
"""
import random
from django.utils import timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


def generate_otp():
    """Generate a random numeric OTP of length defined in settings."""
    start = 10 ** (settings.OTP_LENGTH - 1)
    end = (10 ** settings.OTP_LENGTH) - 1
    return str(random.randint(start, end))


def request_otp(phone: str):
    """Create user if not exists and assign new OTP.
    :param phone: phone number in E.164 format
    :return: user instance"""
    user, _ = User.objects.get_or_create(phone=phone)  # Create user if not exists

    user.otp_code = generate_otp()  # Generate new OTP
    user.otp_created_at = timezone.now()  # Save generation timestamp
    user.save()

    return user


def verify_otp(phone: str, code: str):
    """Verify OTP code and issue JWT tokens.
        :param phone: phone number
        :param code: 4-digit OTP
        :return: dict with access and refresh tokens"""

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        raise ValidationError("Invalid phone or code")

    if user.otp_code != code:  # Check code equality
        raise ValidationError("Invalid code")

    if not user.otp_created_at:  # None treatment
        raise ValidationError("OTP not requested")

    if timezone.now() - user.otp_created_at > settings.OTP_TTL:  # Check expiration (TTL = 5 min)
        raise ValidationError("Code expired")

    # Clear OTP after successful verification
    user.otp_code = ""
    user.otp_created_at = None
    user.is_active = True
    user.save()

    refresh = RefreshToken.for_user(user)  # Issue JWT tokens

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
