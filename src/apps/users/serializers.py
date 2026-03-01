"""Serializers for OTP authentication endpoints. Responsible only for input validation."""
from rest_framework import serializers


class RequestCodeSerializer(serializers.Serializer):
    """Validate phone number for OTP request. Fields: phone (str): Phone number in E.164 format."""
    phone = serializers.CharField(max_length=16)


class VerifyCodeSerializer(serializers.Serializer):
    """Validate phone and OTP code for verification. Fields:
        phone (str): Phone number.
        code (str): OTP code sent via SMS."""
    phone = serializers.CharField(max_length=16)
    code = serializers.CharField(max_length=6)
