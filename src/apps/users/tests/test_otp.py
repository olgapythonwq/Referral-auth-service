from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db  # Разрешает тесту доступ к БД. Поднимает транзакцию и откатывает изменения.
def test_request_code_creates_user(api_client):
    response = api_client.post("/users/auth/request-code/", {"phone": "+79991234567"}, format="json",)

    assert response.status_code == status.HTTP_200_OK
    assert User.objects.filter(phone="+79991234567").exists()


@pytest.mark.django_db
def test_verify_code_returns_tokens(api_client):
    phone = "+79991234567"

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    user = User.objects.get(phone=phone)

    response = api_client.post("/users/auth/verify-code/", {"phone": phone, "code": user.otp_code}, format="json",)

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.json()
    assert "refresh" in response.json()


@pytest.mark.django_db
def test_verify_with_wrong_code_returns_400(api_client):
    phone = "+79990000001"

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    response = api_client.post("/users/auth/verify-code/", {"phone": phone, "code": "000000"}, format="json",)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_verify_with_expired_code_returns_400(api_client):
    phone = "+79990000002"

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    user = User.objects.get(phone=phone)

    # специально "просрочиваем" код
    user.otp_created_at = timezone.now() - timedelta(minutes=10)
    user.save()

    response = api_client.post("/users/auth/verify-code/", {"phone": phone, "code": user.otp_code}, format="json",)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_request_code_twice_generates_new_code(api_client):
    phone = "+79990000003"

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    user = User.objects.get(phone=phone)
    first_code = user.otp_code

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    user.refresh_from_db()
    second_code = user.otp_code

    assert first_code != second_code
