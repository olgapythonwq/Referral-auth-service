import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db  # Разрешает тесту доступ к БД. Поднимает транзакцию и откатывает изменения.

def test_request_code_creates_user(api_client):
    response = api_client.post(
        "/users/auth/request-code/",
        {"phone": "+79991234567"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert User.objects.filter(phone="+79991234567").exists()

@pytest.mark.django_db
def test_verify_code_returns_tokens(api_client):
    phone = "+79991234567"

    api_client.post(
        "/users/auth/request-code/",
        {"phone": phone},
        content_type="application/json",
    )

    user = User.objects.get(phone=phone)

    response = api_client.post(
        "/users/auth/verify-code/",
        {"phone": phone, "code": user.otp_code},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()

@pytest.mark.django_db
def test_verify_with_wrong_code_returns_400(api_client):
    phone = "+79990000001"

    api_client.post(
        "/users/auth/request-code/",
        {"phone": phone},
        content_type="application/json",
    )

    response = api_client.post(
        "/users/auth/verify-code/",
        {"phone": phone, "code": "000000"},
        content_type="application/json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_verify_with_expired_code_returns_400(api_client):
    phone = "+79990000002"

    api_client.post(
        "/users/auth/request-code/",
        {"phone": phone},
        content_type="application/json",
    )

    user = User.objects.get(phone=phone)

    # специально "просрочиваем" код
    user.otp_created_at = timezone.now() - timedelta(minutes=10)
    user.save()

    response = api_client.post(
        "/users/auth/verify-code/",
        {"phone": phone, "code": user.otp_code},
        content_type="application/json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_request_code_twice_generates_new_code(api_client):
    phone = "+79990000003"

    api_client.post(
        "/users/auth/request-code/",
        {"phone": phone},
        content_type="application/json",
    )

    user = User.objects.get(phone=phone)
    first_code = user.otp_code

    api_client.post(
        "/users/auth/request-code/",
        {"phone": phone},
        content_type="application/json",
    )

    user.refresh_from_db()
    second_code = user.otp_code

    assert first_code != second_code
