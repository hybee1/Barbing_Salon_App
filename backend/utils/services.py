from logging import raiseExceptions

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from backend.bookings.models import Booking
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from backend.accounts.models import StaffProfile, User
from backend.exceptions.exceptions import (BookingDateException, UserNotFoundException,
                                           RoleException, UserException, BookingConflictException )
from backend.salon_settings import services_salon_config


class BarberScheduler:

    @staticmethod
    def get_salon_config():
        salon_config = services_salon_config.get_salon_info_config()
        booking_config = services_salon_config.get_salon_booking_config()

        return salon_config, booking_config

    @staticmethod
    def can_receive_bookings(staff: StaffProfile):
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
    def get_this_barber_bookings_for_this_date(self, barber: StaffProfile,
                                               date_utc: date) -> list[Booking]:


        if not self.can_receive_bookings(barber):

            raise UserException('Not a barber or stylist')

        bookings = ( Booking.objects.filter(barber=barber, booking_date=date_utc)
                     .order_by("start_time") )

        return bookings


    # Step 2a. Determine session start by supplying date_time in utc time_zone
    def determine_start(self, session_star_date_time_utc: datetime) -> datetime:

        salon_config, booking_config = self.get_salon_config()

        salon_opening_time = time.fromisoformat( salon_config["open_time"] )
        salon_close_time = time.fromisoformat(salon_config["close_time"])

        salon_timezone = ZoneInfo(salon_config["time_zone"])

        now_utc = timezone.now().astimezone(settings.TIME_ZONE)

        opening_utc = datetime.combine(now_utc.date(), salon_opening_time, tzinfo=ZoneInfo(settings.TIME_ZONE), )

        if session_star_date_time_utc.date() < now_utc.date():

            raise BookingDateException(date)

        # If customer is booking today...
        elif session_star_date_time_utc.date() == now_utc.date():

            _, booking_config = self.get_salon_config()

            interval = int(booking_config["booking_slot_interval"])

            start = max(opening_utc, (now_utc + timedelta(minutes=interval)))

        else: # if date > now.date():

            start = opening_utc

        return self.round_to_booking_interval(start)


    '''
    If now is 10:03
    
    Then start = 10:03
    '''

    # Step 2b. Determine session close by supplying date_time in utc timezone
    def determine_close(self, session_star_date_time_utc: datetime) -> datetime:

        salon_config, _ = self.get_salon_config()

        salon_timezone = ZoneInfo( salon_config["time_zone"] )

        salon_closing_time = time.fromisoformat( salon_config["close_time"] )

        salon_closing = datetime.combine( session_star_date_time_utc.date(), salon_closing_time,
                                          tzinfo=salon_timezone, )

        return salon_closing

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
    def round_to_booking_interval(self, dt: datetime) -> datetime:

        _, booking_config = self.get_salon_config()

        interval = int( booking_config["booking_slot_interval"] )

        if interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero"  )

        minutes = ((dt.minute // interval) + 1) * interval

        if minutes == 60:

            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt + timedelta(hours=1)

        return dt.replace( minute=minutes, second=0, microsecond=0 )


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

    def determine_free_period_for_barber(self, staffProfile_id: int,
                                         session_star_date_time_utc: datetime) -> list[tuple[datetime, datetime]]:


        barber = get_object_or_404(StaffProfile, id=staffProfile_id)

        if not barber:

            raise UserNotFoundException()

        if barber.user.role != User.Role.STAFF:

            raise RoleException()

        if  (not self.can_receive_bookings(barber)):

            raise UserException("Department Exception, this user can render this service")

        try:

            start: datetime = self.determine_start(session_star_date_time_utc)
            closing: datetime = self.determine_close(session_star_date_time_utc)
        except BookingDateException as b_exc:
            raise b_exc

        bookings_for_the_barber: list[Booking] = (
                        self.get_this_barber_bookings_for_this_date(barber, start.date()))

        free_periods: list[tuple[datetime, datetime]] = []
        pointer: datetime = start

        for booking in bookings_for_the_barber:

            if booking.session_start_date_time > pointer:

                free_periods.append(  ( pointer, booking.session_start_date_time )  )

            if booking.session_end_date_time > pointer:

                pointer = booking.session_end_date_time


        if pointer < closing:

            free_periods.append((pointer, closing))

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
    def available_start_time_for_the_service(self, free_periods: list[tuple[datetime, datetime]],
                                             total_service_duration: int) -> list[time] | None:

        salon_info, booking_config = self.get_salon_config()
        salon_timezone = salon_info["time_zone"]

        interval = int( booking_config["booking_slot_interval"]  )

        if interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

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

    def validate_no_overlap(self, barber: StaffProfile, booking_date: date,
                            session_start_date_time: datetime, session_end_date_time: datetime) -> bool:

        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        if not self.can_receive_bookings(barber):
            raise UserException('Selected user can not render this service at staff does not belong '
                                'to the right department')

        with transaction.atomic():
            overlap = (Booking.objects.filter( barber=barber, booking_date=booking_date,
                                            session_start_date_time__lt=session_start_date_time,
                                            session_end_date_time__gt=session_end_date_time
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

    def check_schedule(self, staffProfile_id: int, date1_utc: datetime,  total_service_duration: int):

        try:
            barber_free_periods = self.determine_free_period_for_barber( staffProfile_id, date1_utc )
        except Exception as e:
            raise e

        available_start_time = self.available_start_time_for_the_service(
                                              barber_free_periods, total_service_duration )

        return available_start_time




