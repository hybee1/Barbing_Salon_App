from django.shortcuts import get_object_or_404

from backend.bookings.models import Booking
from backend.accounts.models import StaffProfile, User
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.exceptions.exceptions import (
    BookingDateException,
    RoleException,
    UserException,
    BookingConflictException,
)
from backend.salon_settings import services_salon_config

from datetime import datetime, date, time, timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo


class BarberScheduler:

    # =========================================================
    # SALON CONFIG
    # =========================================================

    @staticmethod
    def get_salon_config():
        salon_config = services_salon_config.get_salon_info_config()
        booking_config = services_salon_config.get_salon_booking_config()

        return salon_config, booking_config

    # =========================================================
    # BARBER ELIGIBILITY
    # =========================================================

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

    # =========================================================
    # STEP 1
    # GET BARBER BOOKINGS FOR A SALON DATE
    # =========================================================

    def get_this_barber_bookings_for_this_date( self, *, barber: StaffProfile,
                                                date_in_salon_tz: date, ) -> list[Booking]:

        if not self.can_receive_bookings(staff=barber):
            raise UserException("Not a barber or stylist")

        ACTIVE_BOOKING_STATUSES = ( Booking.STATUS.PENDING, Booking.STATUS.CONFIRMED,
                                    Booking.STATUS.ARRIVED, Booking.STATUS.IN_PROGRESS,
        )

        return (
            Booking.objects.filter(  barber=barber,  booking_date=date_in_salon_tz,
                                     status__in=ACTIVE_BOOKING_STATUSES
            )
            .order_by("session_start_date_time")
        )

    # =========================================================
    # STEP 2a
    # DETERMINE START OF SCHEDULING WINDOW
    # =========================================================

    def determine_start(
                        self, *, booking_date_in_salon_tz: date, salon_opening_time: time,
                        salon_timezone: ZoneInfo, booking_slot_interval: int, ) -> datetime:

        now_utc = timezone.now()
        now_salon_tz = now_utc.astimezone(salon_timezone)

        if booking_date_in_salon_tz < now_salon_tz.date():
            raise BookingDateException(booking_date_in_salon_tz)

        opening_salon_dt = datetime.combine(
            booking_date_in_salon_tz, salon_opening_time,
        ).replace(tzinfo=salon_timezone)

        # Future date.
        if booking_date_in_salon_tz > now_salon_tz.date():
            return opening_salon_dt

        # Today.
        start = max( opening_salon_dt, now_salon_tz, )

        return self.round_to_booking_interval( dt=start, booking_slot_interval=booking_slot_interval, )

    # =========================================================
    # STEP 2b
    # DETERMINE SALON CLOSE
    # =========================================================

    def determine_close(
                        self, *, booking_date_in_salon_tz: date, salon_closing_time: time,
                        salon_timezone: ZoneInfo, ) -> datetime:

        return datetime.combine( booking_date_in_salon_tz, salon_closing_time, ).replace(tzinfo=salon_timezone)

    # =========================================================
    # STEP 3
    # ROUND TO BOOKING INTERVAL
    # =========================================================

    def round_to_booking_interval(
                                    self,  *, dt: datetime, booking_slot_interval: int, ) -> datetime:

        if booking_slot_interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

        dt = dt.replace( second=0,  microsecond=0, )

        total_minutes = dt.hour * 60 + dt.minute

        remainder = total_minutes % booking_slot_interval

        if remainder == 0:
            return dt

        minutes_to_add = ( booking_slot_interval - remainder )

        return dt + timedelta( minutes=minutes_to_add )

    # =========================================================
    # STEP 4
    # GET BARBER UNAVAILABLE PERIODS
    #
    # This is where BREAK / OFF_DAY / ON_LEAVE /
    # SICK_LEAVE / PERSONAL / OTHER are handled.
    #
    # IMPORTANT:
    #
    # We do NOT use break_date to determine whether the
    # block applies.
    #
    # We compare the actual datetime interval.
    #
    # This allows a block to last:
    #
    #   1 hour
    #   1 day
    #   several days
    #   several weeks
    #   several months
    # =========================================================

    def get_barber_unavailable_periods(
                                        self, *, barber: StaffProfile, schedule_start_utc: datetime,
                                        schedule_end_utc: datetime, ) -> list[tuple[datetime, datetime]]:

        if timezone.is_naive(schedule_start_utc):
            raise ValueError( "schedule_start_utc must be timezone-aware." )

        if timezone.is_naive(schedule_end_utc):
            raise ValueError( "schedule_end_utc must be timezone-aware."  )

        if schedule_start_utc >= schedule_end_utc:
            raise ValueError( "schedule_start_utc must be before schedule_end_utc." )

        blocks = (
            BreakTimeAndOffDays.objects
            .filter(
                staff=barber,

                # Block begins before the schedule ends.
                break_start_date_time__lt=schedule_end_utc,

                # Block ends after the schedule begins.
                break_end_date_time__gt=schedule_start_utc,
            )
            .order_by( "break_start_date_time" )
        )

        unavailable_periods = []

        for block in blocks:

            block_start = block.break_start_date_time
            block_end = block.break_end_date_time

            if timezone.is_naive(block_start):
                raise ValueError( "BreakTimeAndOffDays.break_start_date_time must be timezone-aware." )

            if timezone.is_naive(block_end):
                raise ValueError( "BreakTimeAndOffDays.break_end_date_time must be timezone-aware." )

            if block_start >= block_end:
                continue

            # Clip the block to the current scheduling window.
            clipped_start = max( block_start, schedule_start_utc, )

            clipped_end = min( block_end, schedule_end_utc, )

            if clipped_start < clipped_end:
                unavailable_periods.append(  ( clipped_start,  clipped_end, ) )

        return unavailable_periods

    # =========================================================
    # STEP 5
    # MERGE OVERLAPPING BLOCKED PERIODS
    #
    # Example:
    #
    # ON_LEAVE    10:00 -> 15:00
    # BREAK       12:00 -> 13:00
    #
    # becomes:
    #
    #              10:00 -> 15:00
    #
    # This keeps free-period calculation simple.
    # =========================================================

    @staticmethod
    def merge_periods( periods: list[tuple[datetime, datetime]], ) -> list[tuple[datetime, datetime]]:

        if not periods:
            return []

        sorted_periods = sorted( periods,  key=lambda period: period[0], )

        merged = [ sorted_periods[0] ]

        for current_start, current_end in sorted_periods[1:]:

            last_start, last_end = merged[-1]

            # Overlapping or touching periods.
            if current_start <= last_end:

                merged[-1] = ( last_start, max( last_end, current_end, ), )

            else:
                merged.append( ( current_start, current_end, )  )

        return merged

    # =========================================================
    # STEP 6
    # DETERMINE FREE PERIODS
    #
    # Combines:
    #
    #   1. Existing bookings
    #   2. BREAK
    #   3. OFF_DAY
    #   4. ON_LEAVE
    #   5. SICK_LEAVE
    #   6. PERSONAL
    #   7. OTHER
    #
    # Everything becomes a blocked datetime interval.
    # =========================================================

    def determine_free_period_for_barber(
            self, *, staffProfile_id: int, booking_date_in_salon_tz: date,
            salon_opening_time: time, salon_closing_time: time,
            salon_timezone: ZoneInfo, booking_slot_interval: int, ) -> list[tuple[datetime, datetime]]:

        barber = get_object_or_404(  StaffProfile,  id=staffProfile_id, )

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings( staff=barber ):
            raise UserException( "Department Exception, this user can render this service" )

        # -----------------------------------------------------
        # Determine scheduling window in salon timezone.
        # -----------------------------------------------------

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

        opening_salon = datetime.combine( booking_date_in_salon_tz, salon_opening_time, ).replace( tzinfo=salon_timezone )

        if closing_salon <= opening_salon:
            raise ValueError( "Salon closing time must be later than opening time."  )

        if start_salon >= closing_salon:
            return []

        # -----------------------------------------------------
        # Convert scheduling window to UTC.
        # -----------------------------------------------------

        start_utc = start_salon.astimezone( timezone.utc )

        closing_utc = closing_salon.astimezone( timezone.utc )

        # -----------------------------------------------------
        # EXISTING BOOKINGS
        # -----------------------------------------------------

        bookings_for_the_barber = (
            self.get_this_barber_bookings_for_this_date(
                barber=barber,
                date_in_salon_tz=booking_date_in_salon_tz,
            )
        )

        booking_periods: list[ tuple[datetime, datetime] ] = []

        for booking in bookings_for_the_barber:

            booking_start_utc = ( booking.session_start_date_time  )

            booking_end_utc = (  booking.session_end_date_time )

            if timezone.is_naive( booking_start_utc ):
                raise ValueError( "Booking session_start_date_time must be timezone-aware." )

            if timezone.is_naive( booking_end_utc ):
                raise ValueError( "Booking session_end_date_time must be timezone-aware." )

            if booking_start_utc >= booking_end_utc:
                continue

            # Ignore bookings completely outside
            # the scheduling window.
            if booking_end_utc <= start_utc:
                continue

            if booking_start_utc >= closing_utc:
                continue

            # Clip booking to the scheduling window.
            clipped_start = max( booking_start_utc, start_utc, )

            clipped_end = min( booking_end_utc, closing_utc, )

            if clipped_start < clipped_end:
                booking_periods.append( ( clipped_start, clipped_end, ) )

        # -----------------------------------------------------
        # BREAK / OFF DAY / LEAVE / PERSONAL / ETC.
        # -----------------------------------------------------

        unavailable_periods = (
            self.get_barber_unavailable_periods(
                barber=barber,
                schedule_start_utc=start_utc,
                schedule_end_utc=closing_utc,
            )
        )

        # -----------------------------------------------------
        # COMBINE ALL BLOCKED PERIODS
        # -----------------------------------------------------

        blocked_periods = ( booking_periods + unavailable_periods )

        blocked_periods = self.merge_periods( blocked_periods )

        # -----------------------------------------------------
        # CALCULATE FREE PERIODS
        # -----------------------------------------------------

        free_periods: list[ tuple[datetime, datetime] ] = []

        pointer = start_utc

        for blocked_start, blocked_end in blocked_periods:

            # Block already ended before our pointer.
            if blocked_end <= pointer:
                continue

            # There is free time before this block.
            if blocked_start > pointer:

                free_start = pointer

                free_end = min( blocked_start, closing_utc, )

                if free_start < free_end:
                    free_periods.append( ( free_start, free_end, ) )

            # Move pointer beyond this blocked period.
            if blocked_end > pointer:
                pointer = blocked_end

            # Nothing else can be available.
            if pointer >= closing_utc:
                break

        # -----------------------------------------------------
        # FREE TIME AFTER LAST BLOCK
        # -----------------------------------------------------

        if pointer < closing_utc:

            free_periods.append( ( pointer, closing_utc, )  )

        return free_periods

    # =========================================================
    # STEP 7
    # GENERATE ACTUAL SERVICE START TIMES
    # =========================================================

    def available_start_time_for_the_service_in_salon_tz(
                                        self, *, free_periods: list[tuple[datetime, datetime]],
                                        total_service_duration: int, salon_timezone: ZoneInfo,
                                        booking_slot_interval: int, ) -> list[time]:

        if booking_slot_interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

        if total_service_duration <= 0:
            raise ValueError( "total_service_duration must be greater than zero" )

        duration = timedelta( minutes=total_service_duration )

        interval = timedelta( minutes=booking_slot_interval )

        slots: list[time] = []

        for free_start_utc, free_end_utc in free_periods:

            slot_utc = free_start_utc

            while ( slot_utc + duration <= free_end_utc ):

                slot_salon = slot_utc.astimezone( salon_timezone )

                slots.append( slot_salon.time().replace(  second=0,  microsecond=0,  )  )

                slot_utc += interval

        return slots

    # =========================================================
    # VALIDATE EXISTING BOOKING OVERLAP
    # =========================================================

    def validate_no_overlap(
                            self, *, barber: StaffProfile, booking_date_in_salon_tz: date,
                            session_start_utc: datetime, session_end_utc: datetime,
                            salon_timezone: ZoneInfo,  ) -> bool:

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings( staff=barber  ):
            raise UserException( "Selected user cannot render this service." )

        if timezone.is_naive( session_start_utc  ):
            raise ValueError( "session_start_utc must be timezone-aware." )

        if timezone.is_naive( session_end_utc ):
            raise ValueError( "session_end_utc must be timezone-aware." )

        if session_start_utc >= session_end_utc:
            raise ValueError( "session_start_utc must be before session_end_utc." )

        overlap = (
            Booking.objects
            .filter(
                barber=barber,
                booking_date=booking_date_in_salon_tz,
                status__in=(
                    Booking.STATUS.PENDING,
                    Booking.STATUS.CONFIRMED,
                    Booking.STATUS.ARRIVED,
                    Booking.STATUS.IN_PROGRESS,
                ),

                # Existing booking starts before
                # requested booking ends.
                session_start_date_time__lt=session_end_utc,

                # Existing booking ends after
                # requested booking starts.
                session_end_date_time__gt=session_start_utc,
            )
            .exists()
        )

        if overlap:
            raise BookingConflictException(
                session_start_utc.astimezone(salon_timezone).time(),

                session_end_utc.astimezone(salon_timezone).time(),
            )

        return False

    # =========================================================
    # VALIDATE BREAK / OFF DAY / LEAVE / PERSONAL / OTHER
    # =========================================================

    def validate_no_overlap_with_barber_breaktime_or_off_days(
        self, *, barber: StaffProfile, session_start_utc: datetime,
        session_end_utc: datetime, salon_timezone: ZoneInfo, ) -> bool:

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings( staff=barber ):
            raise UserException( "Selected user cannot render this service." )

        if timezone.is_naive( session_start_utc ):
            raise ValueError( "session_start_utc must be timezone-aware." )

        if timezone.is_naive( session_end_utc ):
            raise ValueError( "session_end_utc must be timezone-aware."  )

        if session_start_utc >= session_end_utc:
            raise ValueError( "session_start_utc must be before session_end_utc." )

        overlap = (
            BreakTimeAndOffDays.objects
            .filter(
                staff=barber,

                # Block begins before booking ends.
                break_start_date_time__lt=session_end_utc,

                # Block ends after booking begins.
                break_end_date_time__gt=session_start_utc,
            )
            .exists()
        )

        if overlap:
            raise BookingConflictException(
                session_start_utc.astimezone(salon_timezone).time(),

                session_end_utc.astimezone(salon_timezone).time(),
            )

        return False

    # =========================================================
    # MAIN PUBLIC SCHEDULER
    # =========================================================

    def check_schedule( self, *, staffProfile_id: int, booking_date_in_salon_tz: date,
                        total_service_duration: int, salon_opening_time: time, salon_closing_time: time,
                        salon_timezone: ZoneInfo, booking_slot_interval: int, ) -> list[time] | None:

        barber_free_periods = (
            self.determine_free_period_for_barber(
                staffProfile_id=staffProfile_id,
                booking_date_in_salon_tz=( booking_date_in_salon_tz ),
                salon_opening_time=( salon_opening_time ),
                salon_closing_time=( salon_closing_time ),
                salon_timezone=salon_timezone,
                booking_slot_interval=( booking_slot_interval ),
            )
        )

        available_start_time = (
            self.available_start_time_for_the_service_in_salon_tz(
                free_periods=barber_free_periods,
                total_service_duration=( total_service_duration ),
                salon_timezone=salon_timezone,
                booking_slot_interval=( booking_slot_interval ),
            )
        )

        return available_start_time
