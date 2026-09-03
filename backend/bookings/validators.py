from django.utils import timezone

from .models import Booking
from staffs.models import StaffSchedule


# CLASS
class BookingValidator:
    """
    Ensures all business rules are respected.
    """

    @staticmethod
    def validate_booking_input(staff, service, booking_date, start_time):
        if not staff.is_active:
            raise ValueError("Staff is not active")

        if not staff.accepting_bookings:
            raise ValueError("Staff not accepting bookings")

        if not service.is_active:
            raise ValueError("Service not active")

        if start_time is None:
            raise ValueError("Start time required")

        if booking_date < timezone.now().date():
            raise ValueError("Cannot book past dates")

    @staticmethod
    def check_overlap(staff, booking_date, start_time, end_time):
        """
        Prevent double booking.
        """

        overlapping = Booking.objects.filter(
            staff=staff,
            booking_date=booking_date
        ).filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping:
            raise ValueError("Time slot already booked")

    @staticmethod
    def validate_staff_schedule(staff, booking_date, start_time, end_time):
        """
        Ensure staff is actually working.
        """

        weekday = booking_date.weekday()

        schedule = StaffSchedule.objects.filter(
            staff=staff,
            day_of_week=weekday,
            is_working=True
        ).first()

        if not schedule:
            raise ValueError("Staff not working on this day")

        if not (schedule.start_time <= start_time <= schedule.end_time):
            raise ValueError("Outside working hours")

