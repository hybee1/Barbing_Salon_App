
from datetime import timedelta, date, datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from backend.accounts.models import StaffProfile
from backend.salon_settings.models import TimeStampedModel




# --------------------
# BARBER BLOCKS (breaks, off days)
# --------------------

class BreakTimeAndOffDays(TimeStampedModel):
# class BreakTimeAndOffDays(models.Model):

    class BlockStatus(models.TextChoices):

        # AVAILABLE = "available", "Available"
        BREAK = "break", "Break"
        OFF_DAY = "off_day", "Off Day"
        ON_LEAVE = "on_leave", "On Leave"
        SICK_LEAVE = "sick_leave", "Sick Leave"
        PERSONAL = "personal", "Personal"
        OTHER = "other", "Other"

    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE, related_name="breaktime_or_off_days"
    )

    # Salon-local calendar date on which this break/off-day will start.
    # it purposely for query convenience. This is intentionally NOT UTC
    break_date = models.DateField()

    # the actual break start time in utc
    break_start_date_time = models.DateTimeField()
    # the actual break start time in utc
    break_end_date_time = models.DateTimeField()

    status = models.CharField( max_length=20, choices=BlockStatus.choices, )

    reason = models.CharField(  max_length=100, blank=True, )

    class Meta:
        verbose_name = "BreakTimeAndOffDays"
        verbose_name_plural = "BreakTimeAndOffDays"
        ordering = ["-break_date", "break_start_date_time"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(break_start_date_time__lt=models.F("break_end_date_time")),
                name="break_start_time_should_before_end",
            ),

        ]

    def clean(self):

        super().clean()

        # Determine the staff member
        if self.staff is None:
            raise ValidationError( {"staff": "A valid staff member is required."} )

        # the immediate two lines below are expected to be in utc as commented in the model
        break_start_date_time_in_utc: datetime = self.break_start_date_time
        break_end_date_time_in_utc: datetime = self.break_end_date_time

        if timezone.is_naive(break_start_date_time_in_utc):
            raise ValidationError({ "break_start_date_time": "Start datetime must be timezone-aware." })

        if timezone.is_naive(break_end_date_time_in_utc):
            raise ValidationError({ "break_end_date_time": "End datetime must be timezone-aware." })


    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)