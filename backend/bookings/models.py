
import uuid

import phonenumbers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import NumberParseException






class Booking(models.Model):

    class STATUS(models.TextChoices):
        ARRIVED = "ARRIVED", "Arrived",
        IN_PROGRESS = "IN_PROGRESS", "In Progress",
        CANCELLED = "CANCELLED", "Cancelled",
        COMPLETED = "COMPLETED", "Completed",
        CONFIRMED = "CONFIRMED", "Confirmed",
        NO_SHOW = "NO_SHOW", "No Show"
        PENDING = "PENDING", "Pending"

    class BookingSource(models.TextChoices):
        ONLINE = "ONLINE", "Online",
        WALK_IN = "WALK_IN", "Walk In"

    booking_reference = models.CharField( max_length=30, unique=True, blank=True )

    barber = models.ForeignKey("accounts.StaffProfile", on_delete=models.CASCADE,
                               related_name="bookings")

    service = models.ForeignKey("services.Service", on_delete=models.CASCADE,
                                related_name="bookings")

    hairstyle = models.ForeignKey("services.Hairstyle", null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name="bookings")

    color = models.ForeignKey("services.Color", null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name="bookings")

    price = models.DecimalField(max_digits = 10, decimal_places = 2, blank=True, null=True )

    customer_name = models.CharField(max_length=100, null=True, blank=True,
                                     validators=[
                                     RegexValidator(
                                         regex=r"^[A-Za-z]+(?: [A-Za-z]+)*$",
                                         message='full_name only support letters and space.'
                                     )
                                 ]
                                     ) # this not a logged-in user so allow
    email = models.EmailField(null=True, blank=True,) # this not a logged-in user so allow

    phone_number =  PhoneNumberField()

    booking_date = models.DateField()

    arrival_time = models.DateTimeField(null=True, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS, default=STATUS.CONFIRMED)

    reason_for_cancellation = models.CharField(max_length=100, null=True, blank=True)

    booking_source = models.CharField(
        max_length=20, choices=BookingSource, default=BookingSource.ONLINE
    )

    booked_by = models.CharField(max_length=15)

    def __str__(self):
        # return f"{self.booking_reference} - {self.customer.full_name}"
        return f"{self.booking_reference} - {self.email}"

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
                {"barber": "Selected user is not a barber."}
            )

        if self.barber and self.barber.department.lower() != 'barber':
            raise ValidationError(
                {"barber": "Selected user does not have te right department."}
            )

        from backend.utils.services import BarberScheduler

        # Validate phone against salon country
        if self.phone_number:
            salon_config, _ = BarberScheduler.get_salon_config()
            country_code = salon_config["country"]

            try:

                phone = phonenumbers.parse( str(self.phone_number), country_code, )

                from backend.exceptions.exceptions import InvalidPhoneNumberError, BookingConflictException

                if not phonenumbers.is_valid_number(phone):
                    raise InvalidPhoneNumberError(str(self.phone_number))

                phone_country = phonenumbers.region_code_for_number(phone)

                if phone_country != country_code:
                    raise InvalidPhoneNumberError(str(self.phone_number))

            except NumberParseException:
                raise ValidationError({ "phone_number": "Invalid phone number." })

            except InvalidPhoneNumberError:
                raise ValidationError({ "phone_number": "Phone number must match the salon's country." })

        try:

            barber_scheduler = BarberScheduler()

            # barber_scheduler.is_overlap( self.barber.user.staff, self.start_time, self.end_time)
            barber_scheduler.is_overlap(self.barber, self.booking_date,
                                        self.start_time, self.end_time)


        except BookingConflictException as exc:

            # raise BookingConflictException( self.start_time, self.end_time)
            raise ValidationError({"start_time": str(exc)})

    def save(self, *args, **kwargs):

        self.full_clean()
        return super().save(*args, **kwargs)

