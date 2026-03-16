import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_request_code_for_existing_user_does_not_create_duplicate(api_client):
    phone = "+79990000004"

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    api_client.post("/users/auth/request-code/", {"phone": phone}, format="json",)

    assert User.objects.filter(phone=phone).count() == 1


@pytest.mark.django_db
def test_profile_requires_authentication(api_client):
    response = api_client.get("/users/api/profile/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
