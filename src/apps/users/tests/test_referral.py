import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_activate_invite_success(api_client):
    inviter = User.objects.create(phone="+79990000010")
    inviter.invite_code = "ABC123"
    inviter.save()

    user = User.objects.create(phone="+79990000011")

    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/users/profile/activate-invite/",
        {"invite_code": "ABC123"},
        content_type="application/json",
    )

    assert response.status_code == 200

    user.refresh_from_db()
    assert user.invited_by == inviter


@pytest.mark.django_db
def test_activate_invite_twice_returns_400(api_client):
    inviter = User.objects.create(phone="+79990000020")
    inviter.invite_code = "XYZ123"
    inviter.save()

    user = User.objects.create(phone="+79990000021")

    api_client.force_authenticate(user=user)

    api_client.post(
        "/users/profile/activate-invite/",
        {"invite_code": "XYZ123"},
        content_type="application/json",
    )

    response = api_client.post(
        "/users/profile/activate-invite/",
        {"invite_code": "XYZ123"},
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_self_invite_returns_400(api_client):
    user = User.objects.create(phone="+79990000030")
    user.invite_code = "SELF01"
    user.save()

    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/users/profile/activate-invite/",
        {"invite_code": "SELF01"},
        content_type="application/json",
    )

    assert response.status_code == 400
