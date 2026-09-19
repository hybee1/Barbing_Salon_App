from logging import raiseExceptions

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404

from backend.bookings.models import Booking
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from backend.accounts.models import StaffProfile, User
from backend.exceptions.exceptions import (BookingDateException, UserNotFoundException,
                                           RoleException, UserException, BookingConflictException)
from backend.salon_settings import services_salon_config


class BarberScheduler:

    @staticmethod
    def get_salon_config():
        salon_config = services_salon_config.get_salon_info_config()
        booking_config = services_salon_config.get_salon_booking_config()

        return salon_config, booking_config

    @staticmethod
    def can_receive_bookings(*, staff: StaffProfile):
        return (
                staff.user.role == User.Role.STAFF
                and staff.user.is_active
                and staff.status == StaffProfile.StaffStatus.ACTIVE
                and staff.department in {
                    StaffProfile.Department.BARBER,
                    StaffProfile.Department.BARBER_STYLIST,
                    StaffProfile.Department.STYLIST,
                }
        )

    # For a particular day:

    # Step 1. Get today's bookings
    def get_this_barber_bookings_for_this_date(self, *, barber: StaffProfile,
                                               date_in_salon_tz: date) -> list[Booking]:

        if not self.can_receive_bookings(staff=barber):
            raise UserException('Not a barber or stylist')

        bookings = (Booking.objects.filter(barber=barber, booking_date=date_in_salon_tz)
                    .order_by("session_start_date_time"))

        return bookings

    # Step 2a. Determine barbing session start by supplying
    def determine_start(self, *, booking_date_in_salon_tz: date, salon_opening_time: time,
                        salon_timezone: ZoneInfo, booking_slot_interval: int) -> datetime:

        salon_opening_date_time_in_salon_tz = datetime.combine(
            booking_date_in_salon_tz, salon_opening_time,
            tzinfo=salon_timezone)

        # this gives instant datetime in utc
        now_utc = timezone.now()
        now_salon_tz = now_utc.astimezone(salon_timezone)

        if salon_opening_date_time_in_salon_tz.date() < now_salon_tz.date():

            raise BookingDateException(date)

        # If customer is booking today...
        elif salon_opening_date_time_in_salon_tz.date() == now_salon_tz.date():

            start = max(salon_opening_date_time_in_salon_tz, now_salon_tz)

        else:  # if session_star_date_time_in_salon_tz.date() > now_salon_tz.date():

            start = salon_opening_date_time_in_salon_tz

        # return start date_time in salon_tz
        return self.round_to_booking_interval(dt=start, booking_slot_interval=booking_slot_interval)

    # Step 2b. Determine salon close
    def determine_close(self, *, booking_date_in_salon_tz: date, salon_closing_time: time,
                        salon_timezone: ZoneInfo) -> datetime:

        salon_closing_date_time_in_salon_tz = datetime.combine(
            booking_date_in_salon_tz, salon_closing_time, tzinfo=salon_timezone)

        # return close date_time in salon_tz
        return salon_closing_date_time_in_salon_tz

    # Step 3. Round to next booking interval
    ''' Usually you don't want customers booking at

    10:03
    10:04
    10:06

    # Instead round to every 5 or 15 minutes.
    # Example (15 minutes):

    10:03 → 10:15
    10:11 →10:15
    10:16 →10:30

    Example function:
    '''

    # the supplied datetime is in utc
    def round_to_booking_interval(self, *, dt: datetime, booking_slot_interval: int) -> datetime:

        interval = booking_slot_interval

        if interval <= 0:
            raise ValueError("booking_slot_interval must be greater than zero")

        minutes = ((dt.minute // interval) + 1) * interval

        if minutes == 60:
            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt + timedelta(hours=1)

        return dt.replace(minute=minutes, second=0, microsecond=0)

    # Then start = round_to_booking_interval(start)
    # If you want 10:10 instead of 10:15, round to 10-minute intervals instead.

    # Step 4. Find free periods
    '''
    Imagine timeline
     9:00 ---------------------------21:30
    Booked

    9:30-10:00
    11:15-12:00
    1:00-1:45
    4:30-5:15

    Walk through bookings.

    '''

    # free_periods = []
    # pointer = start
    # barber_id = could be staffProfile_id or User_id, from ui perspective it should
    # be staffProfile_id

    def determine_free_period_for_barber(self, staffProfile_id: int, booking_date_in_salon_tz: date,
                                         salon_opening_time: time, salon_closing_time: time,
                                         salon_timezone: ZoneInfo,
                                         booking_slot_interval: int) -> list[tuple[datetime, datetime]]:

        barber = get_object_or_404(StaffProfile, id=staffProfile_id)

        if not barber:
            raise UserNotFoundException()

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if (not self.can_receive_bookings(staff=barber)):
            raise UserException("Department Exception, this user can render this service")

        try:

            start: datetime = self.determine_start(booking_date_in_salon_tz=booking_date_in_salon_tz,
                                                   salon_opening_time=salon_opening_time,
                                                   salon_timezone=salon_timezone,
                                                   booking_slot_interval=booking_slot_interval)

            closing: datetime = self.determine_close(booking_date_in_salon_tz=booking_date_in_salon_tz,
                                                     salon_closing_time=salon_closing_time,
                                                     salon_timezone=salon_timezone)
        except BookingDateException as b_exc:
            raise b_exc

        bookings_for_the_barber: list[Booking] = (
            self.get_this_barber_bookings_for_this_date(barber=barber,
                                                        date_in_salon_tz=start.date()))

        free_periods: list[tuple[datetime, datetime]] = []
        pointer: datetime = start.astimezone(ZoneInfo(settings.TIME_ZONE))

        for booking in bookings_for_the_barber:

            if booking.session_start_date_time > pointer:
                free_periods.append((pointer, booking.session_start_date_time))

            if booking.session_end_date_time > pointer:
                pointer = booking.session_end_date_time

        if pointer < closing.astimezone(ZoneInfo(settings.TIME_ZONE)):
            free_periods.append((pointer, closing.astimezone(ZoneInfo(settings.TIME_ZONE))))

        # the free periods are datetime in utc because of session_start_date_time
        # and session_end_date_time
        return free_periods

    # Suppose current time is

    # 10:15

    # You get

    # 10:15 ->11:15

    # 12:00 ->1:00

    # 1:45 ->4:30

    # 5:15 ->9:30

    # Exactly what you want.

    # Step 5. Generate actual booking slots
    '''
    Suppose customer selected

    - Haircut

    - Duration 45 minutes

    - Now generate only slots that fit.

    - Example

    Free

    - 10:15 ->11:15

    Length

    - 60 mins

    Haircut

    - 45 mins

    Possible slots

    - 10:15
    - 10:30

    because 10:45 ->11:30 ❌ exceeds 11:15
    '''

    # Algorithm
    def available_start_time_for_the_service_in_salon_tz(self,
                                                         free_periods: list[tuple[datetime, datetime]],
                                                         total_service_duration: int,
                                                         salon_timezone: ZoneInfo,
                                                         booking_slot_interval: int) -> list[time] | None:

        interval = booking_slot_interval

        if interval <= 0:
            raise ValueError("booking_slot_interval must be greater than zero")

        slots: list[time] = []

        for free_period in free_periods:

            free_start, free_end = free_period

            # because free_start and free_end are still in UTC so convert the to salon time zone
            free_start = free_start.astimezone(salon_timezone)
            free_end = free_end.astimezone(salon_timezone)

            slot = free_start

            while slot + timedelta(minutes=total_service_duration) <= free_end:
                slots.append(slot.time())

                slot += timedelta(minutes=interval)

        return slots

    '''
    If duration is 15 minutes

    then

    10:15

    10:30

    10:45

    11:00

    Example

    Current time

    10:04


    Rounded

    10:15


    Bookings

    9:30-10:00

    11:15-12:00

    1:00-1:45

    Customer selected

    Haircut

    45 mins


    Available slots become

    10:15

    10:30

    12:00

    12:15

    1:45

    2:00

    2:15

    ...

    No clashes.
    '''

    # Prevent Double Booking
    # Even if two customers click 10:15 simultaneously, you must validate again before saving.

    def validate_no_overlap(self, barber: StaffProfile, booking_date_salon_tz: date,
                            session_start_date_time: datetime, session_end_date_time: datetime) -> bool:

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings(staff=barber):
            raise UserException('Selected user can not render this service at staff does not belong '
                                'to the right department')

        with transaction.atomic():
            overlap = (Booking.objects.filter(barber=barber, booking_date=booking_date_salon_tz,
                                              session_start_date_time__lt=session_end_date_time,
                                              session_end_date_time__gt=session_start_date_time
                                              ).exists())

        if overlap:
            raise BookingConflictException(session_start_date_time.time(), session_start_date_time.time())

        return False

    '''
    This overlap rule is the standard interval-overlap check:

    existing.start < new.end
    AND
    existing.end > new.start


    If true, the booking conflicts.
    '''

    def check_schedule(self, staffProfile_id: int,
                       booking_date_in_salon_tz: date, total_service_duration: int,
                       salon_opening_time: time, salon_closing_time: time,
                       salon_timezone: ZoneInfo, booking_slot_interval: int) -> list[time] | None:

        try:
            barber_free_periods = self.determine_free_period_for_barber(
                staffProfile_id=staffProfile_id,
                booking_date_in_salon_tz=booking_date_in_salon_tz,
                salon_opening_time=salon_opening_time,
                salon_closing_time=salon_closing_time,
                salon_timezone=salon_timezone,
                booking_slot_interval=booking_slot_interval)

        except Exception as e:
            raise e

        available_start_time = self.available_start_time_for_the_service_in_salon_tz(
            free_periods=barber_free_periods,
            total_service_duration=total_service_duration,
            salon_timezone=salon_timezone,
            booking_slot_interval=booking_slot_interval)

        return available_start_time
