import pycountry
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from timezone_field import TimeZoneField



from backend.salon_settings.validators import validate_country_code, validate_currency_code


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds
    created and updated timestamps
    to any model that inherits from it.
    """

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SalonInfo(TimeStampedModel):

    salon_name = models.CharField(max_length=255)

    salon_address = models.CharField(max_length=255)
    salon_email = models.EmailField(max_length=255, default="info@salon.com")

    salon_time_zone = TimeZoneField(default="Europe/London")
    salon_country = models.CharField(max_length=2, default="England", validators=[validate_country_code],)
    salon_phone_number = PhoneNumberField()
    salon_currency = models.CharField(max_length=3, default="GBP", validators=[validate_currency_code],)

    salon_open_time = models.TimeField(default="09:00")

    salon_close_time = models.TimeField(default="21:30")

    def clean(self):
        super().clean()

        errors = {}

        # ---------------------------------------------------------
        # Phone number depends on country.
        # ---------------------------------------------------------
        if self.salon_phone_number and self.salon_country:
            from backend.exceptions.exceptions import InvalidPhoneNumberError, InvalidCountryError
            try:
                from backend.salon_settings.services_salon_config import normalize_phone_number
                self.salon_phone_number = normalize_phone_number(
                    value=self.salon_phone_number,
                    country=self.salon_country,
                )
            except ( InvalidCountryError, InvalidPhoneNumberError,  ):
                errors["salon_phone_number"] = ( "Invalid phone number for the selected country." )

        # ---------------------------------------------------------
        # Opening / closing hours.
        # ---------------------------------------------------------
        if (
            self.salon_open_time is not None
            and self.salon_close_time is not None
            and self.salon_close_time <= self.salon_open_time
        ):
            errors["salon_close_time"] = (
                "Close time must be after open time."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def country(self):
        country = pycountry.countries.get(alpha_2=self.salon_country)
        return country.name if country else None

    @property
    def phone_number(self):
        return self.salon_phone_number

    @property
    def time_zone(self):
        timezone = self.salon_time_zone

        return getattr(timezone, "key", timezone)

    @property
    def currency(self):
        return self.salon_currency

    @property
    def email(self):
        return self.salon_email

    @property
    def address(self):
        return self.salon_address

    @property
    def open_time(self):
        return self.salon_open_time

    @property
    def close_time(self):
        return self.salon_close_time


    def __str__(self):
        return self.salon_name

    class Meta:
        verbose_name = "SalonInfo"
        verbose_name_plural = "SalonInfo"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    salon_open_time__lt=models.F("salon_close_time")
                ),
                name="salon_open_before_close",
            ),
        ]


class SalonBookingSetting(TimeStampedModel):
    booking_slot_interval = models.PositiveIntegerField()

    allow_online_booking = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        errors = {}

        if self.booking_slot_interval <= 0:
            errors["booking_slot_interval"] = (
                "Booking slot interval must be greater than zero."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.booking_slot_interval)

    class Meta:
        verbose_name = "SalonBookingSetting"
        verbose_name_plural = "SalonBookingSetting"


