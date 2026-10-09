from zoneinfo import ZoneInfo

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction

from backend.bookings.booking_services import create_booking, update_booking
from backend.bookings.models import Booking
from backend.salon_settings.services_salon_config import get_salon_info_config
from backend.utils.services import BarberScheduler


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Controls how the Booking model appears inside Django Admin.
    """

    list_display = (
        "booking_reference", "get_barber_username", "get_service_name", "get_hairstyle_name",
        "get_color_name", "price", "customer_name", "email", "phone_number", "booking_date",
        "arrival_time", "session_start_date_time", "session_end_date_time", "status",
        "reason_for_cancellation", "booking_source", "booked_by",
    )

    search_fields = (
                       "booking_reference", "barber__user__username", "service__name",
                       "hairstyle__name", "color__name", "customer_name", "email",
                        "phone_number", "booked_by",
    )

    list_filter = ( "status", "booking_source", "booking_date", "barber", )

    ordering = ( "booking_date", "session_start_date_time", )

    @admin.display( description="Barber", ordering="barber__user__username", )
    def get_barber_username(self, obj):
        return obj.barber.user.username

    @admin.display( description="Service", ordering="service__name", )
    def get_service_name(self, obj):
        return obj.service.name

    @admin.display( description="Hairstyle", ordering="hairstyle__name", )
    def get_hairstyle_name(self, obj):
        if obj.hairstyle:
            return obj.hairstyle.name
        return "-"

    @admin.display( description="Color", ordering="color__name", )
    def get_color_name(self, obj):
        if obj.color:
            return obj.color.name
        return "-"

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """
        Create/update a Booking through the booking service layer.

        Creation:
            create_booking()

        Status update:
            update_booking()

        This keeps Admin behavior aligned with the frontend/API.
        """

        # ==========================================================
        # CREATE
        # ==========================================================

        if not change:
            salon_info = get_salon_info_config()

            from zoneinfo import ZoneInfo

            salon_timezone = ZoneInfo( salon_info["time_zone"] )

            # Django Admin has already supplied the datetime values
            # as timezone-aware datetimes according to Django's
            # configured/current timezone.
            #
            # create_booking() expects salon-local datetimes.
            #
            # Therefore, because your project uses TIME_ZONE="UTC",
            # convert the Admin values from UTC to the salon timezone
            # before passing them to create_booking().
            session_start_in_salon_tz = ( obj.session_start_date_time.astimezone( salon_timezone )
            )

            session_end_in_salon_tz = ( obj.session_end_date_time.astimezone( salon_timezone )
            )

            booking = create_booking(
                barber_id=obj.barber.pk, service=obj.service, hairstyle=obj.hairstyle,
                color=obj.color, total_price=obj.price,
                session_start_date_time_in_salon_tz=( session_start_in_salon_tz ),
                session_end_date_time_in_salon_tz=( session_end_in_salon_tz ),
                customer_name=obj.customer_name,
                phone_number=obj.phone_number,
                booking_source=obj.booking_source,
                booked_by=( request.user.username ),
                salon_timezone=salon_timezone,
                status=Booking.STATUS(obj.status),
            )

            # Admin's obj needs to point at the object that was
            # actually created by create_booking().
            obj.pk = booking.pk
            obj.booking_reference = booking.booking_reference

            return

        # ==========================================================
        # UPDATE
        # ==========================================================

        existing_booking = Booking.objects.get( pk=obj.pk  )

        old_status = Booking.STATUS( existing_booking.status  )

        new_status = Booking.STATUS( obj.status )

        # ----------------------------------------------------------
        # Status did not change
        # ----------------------------------------------------------

        if old_status == new_status:
            return

        # ----------------------------------------------------------
        # Status changed
        # ----------------------------------------------------------

        salon_info = get_salon_info_config()

        from zoneinfo import ZoneInfo

        salon_timezone = ZoneInfo( salon_info["time_zone"]  )

        update_booking(
            booking_reference=existing_booking.booking_reference, new_status=new_status,
            reason_for_cancellation=( obj.reason_for_cancellation ),
            salon_timezone=salon_timezone,
        )

    @transaction.atomic
    def delete_model(self, request, obj):
        obj.delete()

    @transaction.atomic
    def delete_queryset(self, request, queryset):
        queryset.delete()