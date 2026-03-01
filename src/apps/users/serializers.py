"""Serializers for OTP authentication endpoints. Responsible only for input validation."""
from rest_framework import serializers

from .models import User


class RequestCodeSerializer(serializers.Serializer):
    """Validate phone number for OTP request. Fields: phone (str): Phone number in E.164 format."""
    phone = serializers.CharField(max_length=16)


class VerifyCodeSerializer(serializers.Serializer):
    """Validate phone and OTP code for verification. Fields:
        phone (str): Phone number.
        code (str): OTP code sent via SMS."""
    phone = serializers.CharField(max_length=16)
    code = serializers.CharField(max_length=6)


class ActivateInviteSerializer(serializers.Serializer):
    """Serializer for activating referral invite code.
    Fields: invite_code (str): referral code to activate"""
    invite_code = serializers.CharField(max_length=6)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for returning user profile data.
    Includes:
        - phone
        - invite_code
        - invited_by (phone)
        - referrals (list of phone numbers)"""
    invited_by = serializers.SerializerMethodField()
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("phone", "invite_code", "invited_by", "referrals",)

    def get_invited_by(self, obj):
        """Return phone number of inviter."""
        if obj.invited_by:
            return obj.invited_by.phone
        return None

    def get_referrals(self, obj):
        """Return list of phone numbers of users invited by current user."""
        return [user.phone for user in obj.referrals.all()]
