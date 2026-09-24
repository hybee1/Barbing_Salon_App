
import uuid
from zoneinfo import ZoneInfo

import phonenumbers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Func, F, Q
from django.utils.dateparse import parse_datetime, parse_date
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import NumberParseException


# class TsRange(Func):
#     function = "TSRANGE"
#     output_field = DateTimeRangeField()

class Booking(models.Model):

    class STATUS(models.TextChoices):
        ARRIVED = "ARRIVED", "Arrived"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"
        CONFIRMED = "CONFIRMED", "Confirmed"
        NO_SHOW = "NO_SHOW", "No Show"
        PENDING = "PENDING", "Pending"

    class BookingSource(models.TextChoices):
        ONLINE = "ONLINE", "Online"
        WALK_IN = "WALK_IN", "Walk In"

    booking_reference = models.CharField( max_length=30, unique=True, )

    barber = models.ForeignKey(
        "accounts.StaffProfile", on_delete=models.CASCADE, related_name="bookings",
    )

    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="bookings",
    )

    hairstyle = models.ForeignKey(
        "services.Hairstyle", null=True,  blank=True, on_delete=models.SET_NULL, related_name="bookings",
    )

    color = models.ForeignKey(
        "services.Color",  null=True,  blank=True, on_delete=models.SET_NULL, related_name="bookings",
    )

    price = models.DecimalField( max_digits=10, decimal_places=2, )

    customer_name = models.CharField( max_length=100, null=True, blank=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+(?: [A-Za-z]+)*$",
                message="full_name only support letters and space.",
            )
        ],
    )

    email = models.EmailField( null=True, blank=True, )

    phone_number = PhoneNumberField()

    # Calendar date in the salon's timezone.
    # This is intentionally NOT UTC and does not represent an instant.
    booking_date = models.DateField()

    # this must be in utc date and time
    session_start_date_time = models.DateTimeField()

    # this must be in utc date and time
    session_end_date_time = models.DateTimeField()

    # this must be in utc date and time
    arrival_time = models.DateTimeField(null=True, blank=True, )

    status = models.CharField( max_length=20, choices=STATUS, default=STATUS.CONFIRMED, )

    reason_for_cancellation = models.CharField( max_length=100,  null=True, blank=True, )

    booking_source = models.CharField( max_length=20, choices=BookingSource, default=BookingSource.ONLINE,  )

    booked_by = models.CharField(  max_length=15, )

    class Meta:
        indexes = [
            models.Index( fields=["barber", "booking_date", "session_start_date_time"]  ),
            models.Index( fields=["booking_date", "status"]  ),
            models.Index( fields=["booking_date", "barber", "status"] ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q( session_start_date_time__lt=F("session_end_date_time") ),
                name="booking_session_start_time_should_before_session_end_time",
            ),
        ]

    def __str__(self):
        # return f"{self.booking_reference} - {self.customer.full_name}"
        return f"{self.booking_reference} - {self.customer_name or self.phone_number}"

    def clean(self):

        super().clean()

        if not self.booking_reference:
            self.booking_reference = f"BK-{uuid.uuid4().hex[:10].upper()}"

        if self.status == self.STATUS.CANCELLED and not self.reason_for_cancellation:
            raise ValidationError(
                "A cancellation reason is required when a booking is cancelled."
            )

        from backend.accounts.models import User

        if self.barber and self.barber.user.role != User.Role.STAFF:
            raise ValidationError(
                {"barber": "Selected user is not a staff member."}
            )

        from backend.utils.services import BarberScheduler

        if self.barber and not BarberScheduler().can_receive_bookings( staff=self.barber):
            raise ValidationError(
                    {"barber": "Selected user does not handle barbing and or styling."}
                )

        # Validate phone against salon country
        if self.phone_number:
            salon_config, _ = BarberScheduler().get_salon_config()
            # salon_timezone = ZoneInfo(salon_config["time_zone"])
            country_code = salon_config["country"]

            try:

                phone = phonenumbers.parse( str(self.phone_number), country_code, )

                from backend.exceptions.exceptions import InvalidPhoneNumberError, BookingConflictException

                if not phonenumbers.is_valid_number(phone):
                    raise InvalidPhoneNumberError(str(self.phone_number))

                phone_country = phonenumbers.region_code_for_number(phone)

                if phone_country != country_code:
                    raise InvalidPhoneNumberError({ "phone_number": f"Phone number {self.phone_number} must "
                                                                    f"match the salon's country." }
                    )

            except NumberParseException:
                raise ValidationError({ "phone_number": "Invalid phone number." })


    def save(self, *args, **kwargs):

        self.full_clean()
        return super().save(*args, **kwargs)

