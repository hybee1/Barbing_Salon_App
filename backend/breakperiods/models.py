from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from backend.accounts.models import StaffProfile
from backend.salon_settings.models import TimeStampedModel

from django.contrib.auth import get_user_model
User = get_user_model()


# --------------------
# BARBER BLOCKS (breaks, off days)
# --------------------

class BreakTimeAndOffDays(TimeStampedModel):
# class BreakTimeAndOffDays(models.Model):

    class BlockStatus(models.TextChoices):

        AVAILABLE = "available", "Available"
        BREAK = "break", "Break"
        OFF_DAY = "off_day", "Off Day"
        ON_LEAVE = "on_leave", "On Leave"
        SICK_LEAVE = "sick_leave", "Sick Leave"
        PERSONAL = "personal", "Personal"
        OTHER = "other", "Other"

    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE, related_name="breaktime_or_off_days"
    )

    date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField( max_length=20, choices=BlockStatus.choices, )

    reason = models.CharField(  max_length=100, blank=True, )

    class Meta:
        verbose_name = "BreakTimeAndOffDays"
        verbose_name_plural = "BreakTimeAndOffDays"
        ordering = ["-date", "start_time"]


    def clean(self):

        super().clean()

        # Determine the staff member
        if self.staff is None:
            raise ValidationError(
                {"staff": "A valid staff member is required."}
            )

        if self.staff.user.role != User.Role.STAFF:
            raise ValidationError(
                {"staff": "Only staff members can have break periods or off days."}
            )

        selected_date = self.date
        start_time = self.start_time
        end_time = self.end_time

        # Date validation
        today_date_and_time = timezone.localtime()
        today_date = today_date_and_time.date()
        current_time = today_date_and_time.time()

        if selected_date < today_date:
            raise ValidationError(
                {"date": "Date cannot be in the past."}
            )

        three_days_ahead = today_date + timedelta(days=3)
        if selected_date > three_days_ahead:
            raise ValidationError(
                {"date": "Date cannot be more than three days ahead."}
            )

        # Time validation
        if end_time <= start_time:
            raise ValidationError(
                {"end_time": "End time must be after start time."}
            )

        # If today, start time must be in the future
        if selected_date == today_date:
            if start_time <= current_time:
                raise ValidationError(
                    {"start_time": "Start time must be after the current time."}
                )

        # if self.status == self.BlockStatus.ON_LEAVE:
        #     days_before_leave = (self.date - today_date).days
        #
        #     if days_before_leave < 3:
        #         raise ValidationError({
        #             "date": "Leave requests must be made at least 3 days before the "
        #                     "leave start date."
        #         })
        #
        #     if days_before_leave > 5:
        #         raise ValidationError({
        #             "date": "Leave requests cannot be made more than 5 days before the "
        #                     "leave start date."
        #         })

        # Overlap validation
        overlap = BreakTimeAndOffDays.objects.filter(
            staff=self.staff,
            date=selected_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.pk:
            overlap = overlap.exclude(pk=self.pk)

        if overlap.exists():
            raise ValidationError(
                "This availability block overlaps with an existing one."
            )

    def save(self, *args, **kwargs):

        # is_new = self.pk is None

        self.full_clean()
        super().save(*args, **kwargs)