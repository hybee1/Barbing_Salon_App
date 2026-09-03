
from django.contrib import admin
from backend.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Controls how the Booking model appears inside the Django Admin.
    """

    list_display = ( "booking_reference", "barber__user__username", "service__name",
                     "hairstyle__name", "price", "customer_name", "email",  "phone_number",
                     "booking_date",  "arrival_time", "start_time",  "end_time",
                     "status",  "reason_for_cancellation", "booking_source",
                     "booked_by",)

    search_fields = ( "booking_reference", "barber__user__username", "booking_date", "status",)

    list_filter = ( "status", "barber__user__username", )

    ordering = ( "booking_date", )

