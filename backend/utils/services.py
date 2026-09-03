from logging import raiseExceptions

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

        print("get_this_barber_bookings_for_this_date 1")
        print("barber = ", barber)
        print("barber department = ", barber.department)

        # barber.department will return the first part which is either value/name not label
        # which is the second
        if not barber.department.lower() in [StaffProfile.Department.BARBER.name.lower(),
                                   StaffProfile.Department.BARBER_STYLIST.name.lower()]:
            print("get_this_barber_bookings_for_this_date 1a")
            raise UserException('Not a barber or stylist')

        bookings = ( Booking.objects.filter(barber=barber, booking_date=date)
                     .order_by("start_time") )

        print("get_this_barber_bookings_for_this_date 2")

        return bookings


    # Step 2a. Determine where "now" starts
    def determine_start(self, date: date) -> datetime:

        print("determine_start 1")

        salon_config, booking_config = self.get_salon_config()
        print("determine_start 1a")
        opening_time = time.fromisoformat( salon_config["open_time"] )

        salon_timezone = ZoneInfo(salon_config["time_zone"])

        opening = datetime.combine( date, opening_time, tzinfo=salon_timezone, )
        print("determine_start 1b")

        now = timezone.now().astimezone(salon_timezone)

        print("determine_start 2")

        if date < now.date():
            print(f"error while determining start_time for this date '{date}' in determine_start")
            raise BookingDateException(date)

        print("determine_start 3")

        # If customer is booking today...
        if date == now.date():
            print("determine_start 3a")
            start = max(opening, (now + timedelta(minutes=15)))

        else: # if date > now.date():
            print("determine_start 3b")
            start = opening

        print("determine_start 4")
        return self.round_to_booking_interval(start)


    '''
    If now is 10:03
    
    Then start = 10:03
    '''

    # Step 2b. Determine where "now" starts
    def determine_close(self, date: date) -> datetime:

        print("determine_close 1")

        salon_config, _ = self.get_salon_config()

        print("determine_close 2")

        salon_timezone = ZoneInfo( salon_config["time_zone"] )

        closing_time = time.fromisoformat( salon_config["close_time"] )
        print("determine_close 3")

        closing = datetime.combine( date, closing_time, tzinfo=salon_timezone, )

        print("determine_close 4")
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

        print("round_to_booking_interval 1")
        _, booking_config = self.get_salon_config()

        interval = int( booking_config["booking_slot_interval"] )
        print("round_to_booking_interval 1a")

        if interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero"  )

        minutes = ((dt.minute // interval) + 1) * interval

        print("round_to_booking_interval 2")
        if minutes == 60:
            print("round_to_booking_interval 2a")
            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt + timedelta(hours=1)

        print("round_to_booking_interval 3")
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

        print("determine_free_period_for_barber 1")
        salon_config, _ = self.get_salon_config()
        salon_timezone = ZoneInfo(salon_config["time_zone"])
        try:
            print("determine_free_period_for_barber 1a")
            start: datetime = self.determine_start(date1)
            closing: datetime = self.determine_close(date1)
        except BookingDateException as b_exc:
            print("determine_free_period_for_barber 1b")
            print("in method determine_free_period in bookings.services.py")
            raise b_exc

        print("determine_free_period_for_barber 2")
        # barber = User.objects.filter(id=barber_id)
        barber = get_object_or_404(StaffProfile, id=staffProfile_id)

        print("determine_free_period_for_barber 3")
        if not barber:
            print("determine_free_period_for_barber 3a")
            raise UserNotFoundException()

        print("determine_free_period_for_barber 4")
        if barber.user.role != User.Role.STAFF:
            print("determine_free_period_for_barber 4a")
            raise RoleException()

        print("determine_free_period_for_barber 5")
        if  (barber.department.lower() not in [StaffProfile.Department.BARBER.name.lower(),
                                                  StaffProfile.Department.BARBER.value.lower(),
                                                  StaffProfile.Department.BARBER.label.lower(),
                                                  StaffProfile.Department.BARBER_STYLIST.name.lower(),
                                                  StaffProfile.Department.BARBER_STYLIST.label.lower(),
                                                  StaffProfile.Department.BARBER_STYLIST.value.lower()]):
            print("determine_free_period_for_barber 5b")
            raise UserException("Department Exception, this user doesn't belong Barber Department")

        print("determine_free_period_for_barber 6")
        bookings_for_the_barber: list[Booking] = (
                        self.get_this_barber_bookings_for_this_date(barber, start.date()))

        print("determine_free_period_for_barber 6a")
        free_periods: list[tuple[datetime, datetime]] = []
        pointer: datetime = start
        # pointer: time = start.time()

        print("determine_free_period_for_barber 7")

        for booking in bookings_for_the_barber:

            print("determine_free_period_for_barber 7a")
            # converted_booking_start_time is datetime
            converted_booking_start_time = datetime.combine(
                            start.date(), booking.start_time, tzinfo=salon_timezone,)

            print("determine_free_period_for_barber 7b")
            # converted_booking_end_time is datetime
            converted_booking_end_time = datetime.combine(
                start.date(), booking.end_time, tzinfo=salon_timezone,)

            print("determine_free_period_for_barber 7c")
            # if booking.start_time > pointer:
            # if booking.start_time > pointer.time():
            if converted_booking_start_time > pointer:
                print("determine_free_period_for_barber 7c 1")
                free_periods.append(

                    ( pointer, converted_booking_start_time )
                )

            print("determine_free_period_for_barber 7d")
            # if booking.end_time > pointer:
            # if booking.end_time > pointer.time():
            if converted_booking_end_time > pointer:
                print("determine_free_period_for_barber 7d 1")
                pointer = converted_booking_end_time

        print("determine_free_period_for_barber 8")
        # if pointer.time() < closing.time():
        # if pointer < closing.time():
        if pointer < closing:
            print("determine_free_period_for_barber 8a")
            free_periods.append((pointer, closing))

        print("determine_free_period_for_barber 9")
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

        print("available_start_time_for_the_service 1")
        _, booking_config = self.get_salon_config()

        interval = int( booking_config["booking_slot_interval"]  )

        if interval <= 0:
            raise ValueError( "booking_slot_interval must be greater than zero" )

        slots: list[time] = []

        print("available_start_time_for_the_service 2")
        for free_period in free_periods:

            print("available_start_time_for_the_service 2a")
            free_start, free_end = free_period
            slot = free_start

            print("available_start_time_for_the_service 2b")
            while slot + timedelta(minutes=total_service_duration) <= free_end:

                print("available_start_time_for_the_service 2b 1")

                slots.append(slot.time())

                print("available_start_time_for_the_service 2b 2")
                slot += timedelta(minutes=15)

        print("available_start_time_for_the_service ")
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
        print("over_lpa 1")
        if barber.user.role != User.Role.STAFF:
            raise RoleException()

        print("barber.user.role", barber.user.role)
        print("over_lpa 2")
        if barber.department.lower() != "barber":
            raise UserException('Not a Barber')

        print("barber.department.lower()", barber.department.lower())
        print("over_lpa 3")
        overlap = (Booking.objects.filter( barber=barber, booking_date=booking_date,
                                          start_time__lt=new_end, end_time__gt=new_start
                                            ).exists())

        print("overlap = ", overlap)
        print("over_lpa 4")
        if overlap:
            print("over_lpa 4a")
            raise BookingConflictException(new_start, new_end)

        print("over_lpa 5")
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




