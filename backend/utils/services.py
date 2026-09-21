from logging import raiseExceptions


from django.shortcuts import get_object_or_404

from backend.bookings.models import Booking
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from backend.accounts.models import StaffProfile, User
from backend.exceptions.exceptions import (BookingDateException,
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
                        salon_timezone: ZoneInfo, booking_slot_interval: int, ) -> datetime:
        """
        Determine the earliest possible booking start.

        The returned datetime is in the salon timezone.

        Rules:
        - Past salon dates are rejected.
        - For a future date, the salon opening time is the first possible slot.
        - For today, use the later of opening time and current salon time,
          then round upward to the next booking interval.
        """
        now_utc = timezone.now()
        now_salon_tz = now_utc.astimezone(salon_timezone)

        if booking_date_in_salon_tz < now_salon_tz.date():
            raise BookingDateException(booking_date_in_salon_tz)

        opening_salon_dt = datetime.combine(
            booking_date_in_salon_tz,
            salon_opening_time,
        ).replace(tzinfo=salon_timezone)

        # Future date:
        # Opening time itself should be a valid starting point.
        if booking_date_in_salon_tz > now_salon_tz.date():
            return opening_salon_dt

        # Today:
        # Do not allow a time before opening.
        start = max(opening_salon_dt, now_salon_tz)

        return self.round_to_booking_interval(dt=start, booking_slot_interval=booking_slot_interval, )

    # Step 2b. Determine salon close
    def determine_close( self, *, booking_date_in_salon_tz: date,
                        salon_closing_time: time, salon_timezone: ZoneInfo, ) -> datetime:
        """
        Construct the salon's closing boundary for the specified
        salon calendar date.

        Returned datetime is in the salon timezone.
        """
        return datetime.combine( booking_date_in_salon_tz, salon_closing_time, ).replace(tzinfo=salon_timezone)

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
    def round_to_booking_interval( self, *, dt: datetime, booking_slot_interval: int, ) -> datetime:
        """
        Round a salon-local datetime upward to the next booking interval.

        Examples with a 15-minute interval:

            09:00:00 -> 09:00
            09:01:00 -> 09:15
            09:03:00 -> 09:15
            09:14:59 -> 09:15
            09:15:00 -> 09:15
            09:16:00 -> 09:30
        """
        if booking_slot_interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

        # Remove seconds/microseconds first.
        dt = dt.replace(second=0, microsecond=0)

        total_minutes = dt.hour * 60 + dt.minute
        remainder = total_minutes % booking_slot_interval

        if remainder == 0:
            return dt

        minutes_to_add = booking_slot_interval - remainder

        return dt + timedelta(minutes=minutes_to_add)

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

    def determine_free_period_for_barber(
            self, *, staffProfile_id: int, booking_date_in_salon_tz: date,
            salon_opening_time: time, salon_closing_time: time,
            salon_timezone: ZoneInfo, booking_slot_interval: int, ) -> list[tuple[datetime, datetime]]:

        barber = get_object_or_404( StaffProfile, id=staffProfile_id, )

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings(staff=barber):
            raise UserException(
                "Department Exception, this user can render this service"
            )

        start_salon = self.determine_start(
            booking_date_in_salon_tz=booking_date_in_salon_tz,
            salon_opening_time=salon_opening_time,
            salon_timezone=salon_timezone,
            booking_slot_interval=booking_slot_interval,
        )

        closing_salon = self.determine_close(
            booking_date_in_salon_tz=booking_date_in_salon_tz,
            salon_closing_time=salon_closing_time,
            salon_timezone=salon_timezone,
        )

        opening_salon = datetime.combine(
            booking_date_in_salon_tz, salon_opening_time, ).replace(tzinfo=salon_timezone)

        if closing_salon <= opening_salon:
            raise ValueError( "Salon closing time must be later than opening time." )

        # Convert business boundaries to UTC.
        #
        # From this point onward, all interval arithmetic is done in UTC.
        start_utc = start_salon.astimezone(timezone.utc)
        closing_utc = closing_salon.astimezone(timezone.utc)

        # The salon-local booking date is authoritative.
        bookings_for_the_barber = (
            self.get_this_barber_bookings_for_this_date(
                barber=barber, date_in_salon_tz=booking_date_in_salon_tz, )
        )

        free_periods: list[tuple[datetime, datetime]] = []

        pointer = start_utc

        for booking in bookings_for_the_barber:
            booking_start_utc = booking.session_start_date_time
            booking_end_utc = booking.session_end_date_time

            # Ignore bookings that ended before our scheduling window.
            if booking_end_utc <= pointer:
                continue

            # There is free time before this booking.
            if booking_start_utc > pointer:
                free_start = pointer
                free_end = min( booking_start_utc, closing_utc,  )

                if free_start < free_end:
                    free_periods.append( (free_start, free_end)  )

            # Move the pointer past this booking.
            if booking_end_utc > pointer:
                pointer = booking_end_utc

            # No need to process bookings after closing.
            if pointer >= closing_utc:
                break

        # There is free time after the final booking.
        if pointer < closing_utc:
            free_periods.append( (pointer, closing_utc) )

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
    def available_start_time_for_the_service_in_salon_tz(
            self, *, free_periods: list[tuple[datetime, datetime]],
            total_service_duration: int, salon_timezone: ZoneInfo,
            booking_slot_interval: int, ) -> list[time]:

        if booking_slot_interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

        if total_service_duration <= 0:
            raise ValueError( "total_service_duration must be greater than zero" )

        duration = timedelta( minutes=total_service_duration  )

        interval = timedelta(  minutes=booking_slot_interval )

        slots: list[time] = []

        for free_start_utc, free_end_utc in free_periods:

            slot_utc = free_start_utc

            while ( slot_utc + duration <= free_end_utc ):
                slot_salon = slot_utc.astimezone( salon_timezone )

                slots.append( slot_salon.time().replace( second=0, microsecond=0, )  )

                slot_utc += interval

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

    def validate_no_overlap( self, *, barber: StaffProfile, booking_date_in_salon_tz: date,
                             session_start_utc: datetime, session_end_utc: datetime,
                             salon_timezone: ZoneInfo,) -> bool:

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings(staff=barber):
            raise UserException( "Selected user cannot render this service." )

        if timezone.is_naive(session_start_utc):
            raise ValueError( "session_start_utc must be timezone-aware."  )

        if timezone.is_naive(session_end_utc):
            raise ValueError( "session_end_utc must be timezone-aware." )

        overlap = Booking.objects.filter(
            barber=barber, booking_date=booking_date_in_salon_tz,
            session_start_date_time__lt=session_end_utc,
            session_end_date_time__gt=session_start_utc,
        ).exists()

        if overlap:
            raise BookingConflictException(
                session_start_utc.astimezone(salon_timezone).time(),
                session_end_utc.astimezone(salon_timezone).time(),
            )

        return False

    '''
    This overlap rule is the standard interval-overlap check:

    existing.start < new.end
    AND
    existing.end > new.start


    If true, the booking conflicts.
    '''

    '''
    validate no overlap with barber's breaktime or off days 
    '''
    def validate_no_overlap_with_barber_breaktime_or_off_days( self, *, barber: StaffProfile,
                                                                booking_date_in_salon_tz: date,
                             session_start_utc: datetime, session_end_utc: datetime,
                             salon_timezone: ZoneInfo,) -> bool:

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings(staff=barber):
            raise UserException( "Selected user cannot render this service." )

        if timezone.is_naive(session_start_utc):
            raise ValueError( "session_start_utc must be timezone-aware."  )

        if timezone.is_naive(session_end_utc):
            raise ValueError( "session_end_utc must be timezone-aware." )

        overlap = Booking.objects.filter(
            barber=barber, booking_date=booking_date_in_salon_tz,
            session_start_date_time__lt=session_end_utc,
            session_end_date_time__gt=session_start_utc,
        ).exists()

        if overlap:
            raise BookingConflictException(
                session_start_utc.astimezone(salon_timezone).time(),
                session_end_utc.astimezone(salon_timezone).time(),
            )

        return False


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
