
import pytest
from rest_framework.test import APIClient

from backend.accounts.models import User, StaffProfile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    user = User.objects.create_user(
        username="customer1",
        email="customer@example.com",
        password="StrongPassword123!",
        role=User.Role.CUSTOMER,
        phone_number="+2348012345678",
    )
    return user


@pytest.fixture
def staff(db):
    user = User.objects.create_user(
        username="barber1",
        email="barber@example.com",
        password="StrongPassword123!",
        role=User.Role.STAFF,
        phone_number="+2348012345679",
    )

    StaffProfile.objects.create(
        user=user,
        department=StaffProfile.Department.BARBER,
        position=StaffProfile.Position.LEVEL_ONE,
        status=StaffProfile.StaffStatus.ACTIVE,
    )

    return user


@pytest.fixture
def manager(db):
    user = User.objects.create_user(
        username="manager1",
        email="manager@example.com",
        password="StrongPassword123!",
        role=User.Role.STAFF_ADMIN,
        phone_number="+2348012345680",
    )

    from django.contrib.auth.models import Group

    group, _ = Group.objects.get_or_create(name="manager")
    user.groups.add(group)

    return user
