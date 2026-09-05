from pathlib import Path
from uuid import uuid4

import phonenumbers

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import NumberParseException



from core_config import settings_base


def get_photo_upload_path(obj, filename):
    extension = Path(filename).suffix.lower()
    filename = f"{uuid4().hex}{extension}"

    if obj.role == User.Role.STAFF:
        folder = "staff"

    elif obj.role == User.Role.STAFF_ADMIN:
        folder = "staff_admins"

    else:
        folder = "customers"

    return f"{folder}/{filename}"


class User(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        STAFF = "staff", "Staff"
        STAFF_ADMIN = "staff_admin", "Staff Admin"

        @classmethod
        def is_obj_of_role(cls, name_role: str):
            for role in User.Role:
                if name_role.lower() in [role.name.lower(),
                                         role.value.lower(), role.label.lower()]:
                    return role

            raise ValidationError(f"Role '{name_role}' not a valid role.")

    role = models.CharField( max_length=20, choices=Role.choices, )

    phone_number = PhoneNumberField()

    image = models.ImageField(upload_to=get_photo_upload_path, blank=True, null=True)


    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        return None

    def __str__(self):
        return self.get_full_name() or self.username

    def clean(self):
        super().clean()
        # Validate phone against salon country
        if self.phone_number:

            from backend.utils.services import BarberScheduler
            from backend.exceptions.exceptions import InvalidPhoneNumberError

            salon_config, _ = BarberScheduler().get_salon_config()
            country_code = salon_config["country"]

            try:
                phone = phonenumbers.parse(str(self.phone_number), country_code, )

                if not phonenumbers.is_valid_number(phone):
                    raise InvalidPhoneNumberError(str(self.phone_number))

                phone_country = phonenumbers.region_code_for_number(phone)

                if phone_country != country_code:
                    raise InvalidPhoneNumberError(str(self.phone_number))

            except NumberParseException:
                raise ValidationError({"phone_number": "Invalid phone number."})

            except InvalidPhoneNumberError:
                raise ValidationError({"phone_number": "Phone number must match the salon's country."})

    class Meta:
        verbose_name = "User"

        verbose_name_plural = "Users"

        ordering = ["date_joined"]

    REQUIRED_FIELDS = ["email", "role", "phone_number"]


class CustomerProfile(models.Model):

    user = models.OneToOneField(settings_base.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="customer")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["-user__date_joined"]


class StaffProfile(models.Model):

    class Department(models.TextChoices):
        ADMIN = "admin", "Admin"
        RECEPTION = "reception", "Reception"
        BARBER = "barber", "Barber"
        STYLIST = "stylist", "Stylist"
        BARBER_STYLIST = "Barber_Stylist", "Barber & Stylist"

        @classmethod
        def is_obj_of_department(cls, name_role: str):
            for dept in StaffProfile.Department:
                if name_role.lower() in [dept.label.lower(), dept.name.lower(),
                                         dept.value.lower()]:
                    return dept
            raise ValidationError(f"Department '{name_role}' not found.")

    class Position(models.TextChoices):
        LEVEL_ONE = "level_1", "Level one"
        LEVEL_TWO = "level_2", "level two"
        SENIOR = "senior", "Senior"

        @classmethod
        def is_obj_of_position(cls, name_role: str):
            for pos in StaffProfile.Position:
                if name_role.lower() in [pos.name.lower(),
                                         pos.value.lower(), pos.label.lower()]:
                    return pos
            raise ValidationError(f"Position '{name_role}' not found.")

    class StaffStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        RESIGNED = "resigned", "Resigned"
        TERMINATED = "terminated", "Terminated"
        ON_LEAVE = "on_leave", "On Leave"

        @classmethod
        def is_obj_of_staff_status(cls, name_role: str):
            for status in StaffProfile.StaffStatus:
                if name_role.lower()  in [status.name.lower(),
                                          status.value.lower(), status.label.lower()] :

                    return status

            raise ValidationError(f"StaffStatus '{name_role}' not found.")


    user = models.OneToOneField(settings_base.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="staffprofile")

    department = models.CharField(max_length=35, choices=Department.choices,
                                  default=Department.BARBER, )

    position = models.CharField(max_length=35, choices=Position.choices,
                                            default=Position.LEVEL_ONE,)

    employment_date = models.DateField( default=timezone.localdate,)

    status = models.CharField(max_length=35, choices=StaffStatus.choices,
                                            default=StaffStatus.ACTIVE,)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staffs"
        ordering = ["user__date_joined"]





