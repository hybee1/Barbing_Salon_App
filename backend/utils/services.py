from logging import raiseExceptions

from django.db import transaction
from django.shortcuts import get_object_or_404

from backend.bookings.models import Booking
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from backend.accounts.models import StaffProfile, User
from backend.exceptions.exceptions import (BookingDateException, UserNotFoundException,
                                           RoleException, UserException, BookingConflictException )
from backend.salon_settings import services_salon_config


class BarberScheduler:

    def get_salon_config(self):
        salon_config = services_salon_config.get_salon_info_config()
        booking_config = services_salon_config.get_salon_booking_config()

        return salon_config, booking_config

    # For a particular day:

    # Step 1. Get today's bookings
    def get_this_barber_bookings_for_this_date(self, barber: StaffProfile,
                                               date: date) -> list[Booking]:



        # barber.department will return the first part which is either value/name not label
        # which is the second
        if not barber.department.lower() in [StaffProfile.Department.BARBER.name.lower(),
                                   StaffProfile.Department.BARBER_STYLIST.name.lower()]:

            raise UserException('Not a barber or stylist')

        bookings = ( Booking.objects.filter(barber=barber, booking_date=date)
                     .order_by("start_time") )

        return bookings


    # Step 2a. Determine where "now" starts
    def determine_start(self, date: date) -> datetime:

        salon_config, booking_config = self.get_salon_config()

        opening_time = time.fromisoformat( salon_config["open_time"] )

        salon_timezone = ZoneInfo(salon_config["time_zone"])

        opening = datetime.combine( date, opening_time, tzinfo=salon_timezone, )

        now = timezone.now().astimezone(salon_timezone)

        if date < now.date():

            raise BookingDateException(date)

        # If customer is booking today...
        if date == now.date():

            start = max(opening, (now + timedelta(minutes=15)))

        else: # if date > now.date():

            start = opening

        return self.round_to_booking_interval(start)


    '''
    If now is 10:03
    
    Then start = 10:03
    '''

    # Step 2b. Determine where "now" starts
    def determine_close(self, date: date) -> datetime:

        salon_config, _ = self.get_salon_config()

        salon_timezone = ZoneInfo( salon_config["time_zone"] )

        closing_time = time.fromisoformat( salon_config["close_time"] )

        closing = datetime.combine( date, closing_time, tzinfo=salon_timezone, )

        return closing

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
    # def round_to_next_15(self, dt: datetime) -> datetime:
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
                                         date1: date) -> list[tuple[datetime, datetime]]:

        salon_config, _ = self.get_salon_config()
        salon_timezone = ZoneInfo(salon_config["time_zone"])
        try:

            start: datetime = self.determine_start(date1)
            closing: datetime = self.determine_close(date1)
        except BookingDateException as b_exc:


            raise b_exc

        # barber = User.objects.filter(id=barber_id)
        barber = get_object_or_404(StaffProfile, id=staffProfile_id)

        if not barber:

            raise UserNotFoundException()

        if barber.user.role != User.Role.STAFF:

            raise RoleException()

        if  (barber.department.lower() not in [StaffProfile.Department.BARBER.name.lower(),
                                                  StaffProfile.Department.BARBER.value.lower(),
                                                  StaffProfile.Department.BARBER.label.lower(),
                                                  StaffProfile.Department.BARBER_STYLIST.name.lower(),
                                                  StaffProfile.Department.BARBER_STYLIST.label.lower(),
                                                  StaffProfile.Department.BARBER_STYLIST.value.lower()]):

            raise UserException("Department Exception, this user doesn't belong Barber Department")

        bookings_for_the_barber: list[Booking] = (
                        self.get_this_barber_bookings_for_this_date(barber, start.date()))

        free_periods: list[tuple[datetime, datetime]] = []
        pointer: datetime = start
        # pointer: time = start.time()

        for booking in bookings_for_the_barber:

            # converted_booking_start_time is datetime
            converted_booking_start_time = datetime.combine(
                            start.date(), booking.start_time, tzinfo=salon_timezone,)

            # converted_booking_end_time is datetime
            converted_booking_end_time = datetime.combine(
                start.date(), booking.end_time, tzinfo=salon_timezone,)

            # if booking.start_time > pointer:
            # if booking.start_time > pointer.time():
            if converted_booking_start_time > pointer:

                free_periods.append(

                    ( pointer, converted_booking_start_time )
                )

            # if booking.end_time > pointer:
            # if booking.end_time > pointer.time():
            if converted_booking_end_time > pointer:

                pointer = converted_booking_end_time

        # if pointer.time() < closing.time():
        # if pointer < closing.time():
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

        _, booking_config = self.get_salon_config()

        interval = int( booking_config["booking_slot_interval"]  )

        if interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

        slots: list[time] = []

        for free_period in free_periods:

            free_start, free_end = free_period
            slot = free_start

            while slot + timedelta(minutes=total_service_duration) <= free_end:

                slots.append(slot.time())

                slot += timedelta(minutes=15)

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

    def is_overlap(self, barber: StaffProfile, booking_date: date,
        new_start: time, new_end: time) -> bool:

        # if barber.user.role != User.Role.BARBER:
        #     raise RoleException()

        if barber.user.role != User.Role.STAFF:
            raise RoleException()


        if barber.department.lower() != "barber":
            raise UserException('Not a Barber')

        with transaction.atomic():
            overlap = (Booking.objects.filter( barber=barber, booking_date=booking_date,
                                            start_time__lt=new_end, end_time__gt=new_start
                                                ).exists())


        if overlap:

            raise BookingConflictException(new_start, new_end)

        return False

    '''
    This overlap rule is the standard interval-overlap check:
    
    existing.start < new.end
    AND
    existing.end > new.start
    
    
    If true, the booking conflicts.
    '''

    def check_schedule(self, staffProfile_id: int, date1: date,  total_service_duration: int):

        try:
            barber_free_periods = self.determine_free_period_for_barber(
                                                        staffProfile_id, date1)
        except Exception as e:
            raise e

        available_start_time = self.available_start_time_for_the_service(
                                              barber_free_periods, total_service_duration )

        return available_start_time




