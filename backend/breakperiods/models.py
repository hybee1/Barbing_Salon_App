
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

    # Calendar date in the salon's timezone.
    # This is intentionally NOT UTC and does not represent an instant.
    break_date = models.DateField()

    break_start_date_time = models.DateTimeField()
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
            raise ValidationError(
                {"staff": "A valid staff member is required."}
            )

        selected_date: date = self.break_date
        break_start_date_time: datetime = self.break_start_date_time
        break_end_date_time: datetime  = self.break_end_date_time

        if timezone.is_naive(break_start_date_time):
            raise ValidationError({
                "break_start_date_time": "Start datetime must be timezone-aware."
            })

        if timezone.is_naive(break_end_date_time):
            raise ValidationError({
                "break_end_date_time": "End datetime must be timezone-aware."
            })

        from backend.utils.services import BarberScheduler

        salon_config, booking_config = BarberScheduler().get_salon_config()

        salon_timezone = ZoneInfo(salon_config["time_zone"])
        salon_open_time = booking_config["open_time"]
        salon_close_time = booking_config["close_time"]

        start_salon = break_start_date_time.astimezone(salon_timezone)
        end_salon = break_end_date_time.astimezone(salon_timezone)

        start_time = start_salon.time()
        end_time = end_salon.time()

        if start_time < salon_open_time:
            raise ValidationError({ "details": "Break cannot start before salon opening time." })

        if end_time > salon_close_time:
            raise ValidationError({ "details": "Break cannot end after salon closing time." })

        now_utc = timezone.now()
        now_salon = now_utc.astimezone(salon_timezone)

        today_date = now_salon.date()

        if selected_date < today_date:
            raise ValidationError(
                {"date": "Date cannot be in the past."}
            )

        three_days_ahead = today_date + timedelta(days=3)

        if selected_date > three_days_ahead:
            raise ValidationError(
                {"date": "Date cannot be more than three days ahead."}
            )

        if break_end_date_time <= break_start_date_time:
            raise ValidationError(
                {"end_time": "End time must be after start time."}
            )

        try:
            break_status_enum = BreakTimeAndOffDays.BlockStatus(self.status)

        except ValueError:
            raise ValidationError({ "details": "Invalid break status." })

        if break_status_enum in { BreakTimeAndOffDays.BlockStatus.OFF_DAY, BreakTimeAndOffDays.BlockStatus.ON_LEAVE,
                            BreakTimeAndOffDays.BlockStatus.SICK_LEAVE, BreakTimeAndOffDays.BlockStatus.PERSONAL,
                            BreakTimeAndOffDays.BlockStatus.OTHER,
        }:

            if (break_end_date_time - break_start_date_time < timedelta(hours=6)):
                raise ValidationError({"details": "duration can not be less than six hours."})

        if break_status_enum == BreakTimeAndOffDays.BlockStatus.BREAK:

            if start_salon.date() != selected_date:
                raise ValidationError({ "break_date": "Break start date and time must be on same day as"
                                                      " the selected date."})

            if end_salon.date() != selected_date:
                raise ValidationError({ "break_date": "Break end datetime must belong to the selected date." })



            if selected_date == today_date:
                break_start_in_salon_tz = (
                    break_start_date_time.astimezone(salon_timezone)
                )

                if break_start_in_salon_tz <= now_salon:
                    raise ValidationError( { "start_time": "Start time must be after the current time." } )

        # Overlap validation
        overlap = BreakTimeAndOffDays.objects.filter(
            staff=self.staff,
            break_date=selected_date,
            break_start_date_time__lt=break_end_date_time,
            break_end_date_time__gt=break_start_date_time,
        )

        if self.pk:
            overlap = overlap.exclude(pk=self.pk)

        if overlap.exists():
            raise ValidationError( {
                "details": "This availability block overlaps with an existing one." })

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)