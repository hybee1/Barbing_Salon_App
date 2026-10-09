from zoneinfo import ZoneInfo

from django.contrib import admin
from django.db import transaction

from backend.breakperiods.break_periods_services import create_break_period
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.salon_settings.services_salon_config import (
    get_salon_info_config,
)


@admin.register(BreakTimeAndOffDays)
class BreakTimeAndOffDaysAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for BreakTimeAndOffDays.

    Creation is delegated to create_break_period() so that the
    Admin and frontend/API use the same business logic.

    Django is configured with:

        TIME_ZONE = "UTC"
        USE_TZ = True

    Therefore Django Admin supplies timezone-aware datetime values
    in UTC.

    create_break_period(), however, expects salon-local datetimes.

    Therefore, before calling create_break_period(), the Admin
    datetime values are converted from UTC to the salon timezone.
    """

    list_display = (
        "get_staff_username",
        "get_staff_department",
        "break_date",
        "break_start_date_time",
        "break_end_date_time",
        "status",
        "reason",
    )

    search_fields = (
        "staff__user__username",
        "staff__department",
        "break_date",
        "break_start_date_time",
        "break_end_date_time",
        "status",
        "reason",
    )

    list_filter = (
        "staff__department",
        "status",
        "break_date",
    )

    ordering = (
        "break_date",
        "break_start_date_time",
    )

    @admin.display(
        description="Staff",
        ordering="staff__user__username",
    )
    def get_staff_username(self, obj):
        return obj.staff.user.username

    @admin.display(
        description="Department",
        ordering="staff__department",
    )
    def get_staff_department(self, obj):
        return obj.staff.department

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """
        Create/update a BreakTimeAndOffDays object.

        Creation is delegated to create_break_period().

        This ensures Admin and frontend/API share the same
        creation logic.

        IMPORTANT:

        Django Admin provides the DateTimeField values according
        to Django's configured timezone.

        With:

            TIME_ZONE = "UTC"
            USE_TZ = True

        the values received here are UTC-aware datetimes.

        create_break_period() expects salon-local datetimes.

        Therefore:

            Admin UTC datetime
                    ↓
            convert to salon timezone
                    ↓
            create_break_period()
                    ↓
            convert salon datetime back to UTC
                    ↓
            save to database
        """

        # ==========================================================
        # CREATE
        # ==========================================================

        if not change:

            salon_info = get_salon_info_config()

            salon_timezone = ZoneInfo(
                salon_info["time_zone"]
            )

            # ------------------------------------------------------
            # Convert Admin UTC datetime to salon-local datetime.
            # ------------------------------------------------------

            break_start_in_salon_tz = (
                obj.break_start_date_time.astimezone(
                    salon_timezone
                )
            )

            break_end_in_salon_tz = (
                obj.break_end_date_time.astimezone(
                    salon_timezone
                )
            )

            # ------------------------------------------------------
            # Delegate creation to the service layer.
            # ------------------------------------------------------

            break_period = create_break_period(
                staff_id=obj.staff.pk,

                break_start_date_time_in_salon_tz=(
                    break_start_in_salon_tz
                ),

                break_end_date_time_in_salon_tz=(
                    break_end_in_salon_tz
                ),

                status=obj.status,
                reason=obj.reason,
            )

            # ------------------------------------------------------
            # Make the Admin object reference the object that was
            # actually created by create_break_period().
            # ------------------------------------------------------

            obj.pk = break_period.pk

            return

        # ==========================================================
        # UPDATE
        # ==========================================================

        raise NotImplementedError(
            "Updating BreakTimeAndOffDays from Django Admin is "
            "not currently supported. Please implement an "
            "update_break_period() service before enabling Admin "
            "updates."
        )