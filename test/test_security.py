
import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_anonymous_user_cannot_access_staff_api(api_client):
    response = api_client.get("/api/staffs/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_staff_can_access_authenticated_staff_endpoint(api_client, staff):
    api_client.force_authenticate(user=staff)

    response = api_client.get("/api/staffs/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_customer_cannot_access_staff_endpoint(api_client, customer):
    api_client.force_authenticate(user=customer)

    response = api_client.get("/api/staffs/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_login_rejects_wrong_password(api_client, staff):
    response = api_client.post(
        "/api/staff/login/",
        {
            "username": staff.username,
            "password": "WRONG PASSWORD",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_does_not_expose_password(api_client, staff):
    response = api_client.post(
        "/api/staff/login/",
        {
            "username": staff.username,
            "password": "StrongPassword123!",
        },
        format="json",
    )

    assert "password" not in response.data


@pytest.mark.django_db
def test_security_headers_in_production(settings):
    settings.DEBUG = False
    settings.SECURE_SSL_REDIRECT = True
    settings.SECURE_HSTS_SECONDS = 31536000

    assert settings.DEBUG is False
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SECURE_HSTS_SECONDS > 0
