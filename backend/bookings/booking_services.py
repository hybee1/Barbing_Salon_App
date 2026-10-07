
from datetime import datetime, timezone as dt_timezone, date
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from backend.accounts.models import StaffProfile
from backend.bookings.models import Booking
from backend.exceptions.exceptions import BookingException
from backend.salon_settings.services_salon_config import get_salon_info_config
from backend.services.models import Service, Hairstyle, Color
from backend.utils.services import BarberScheduler, convert_utc_iso_to_salon_time


ALLOWABLE_BOOKING_STATUS_CHANGES = {
    Booking.STATUS.ARRIVED.value: (Booking.STATUS.COMPLETED.value, Booking.STATUS.CANCELLED.value,),
    Booking.STATUS.IN_PROGRESS.value: (Booking.STATUS.COMPLETED.value, Booking.STATUS.CANCELLED.value,),
    Booking.STATUS.CANCELLED.value: (),
    Booking.STATUS.COMPLETED.value: (),
    Booking.STATUS.CONFIRMED.value: (Booking.STATUS.COMPLETED.value, Booking.STATUS.NO_SHOW.value,
                                     Booking.STATUS.CANCELLED.value,),
    Booking.STATUS.NO_SHOW.value: (),
    Booking.STATUS.PENDING.value: (Booking.STATUS.CONFIRMED.value, Booking.STATUS.COMPLETED.value,
                                   Booking.STATUS.CANCELLED.value),
}


def allowable_status_change(*, old_status: Booking.STATUS, new_status: Booking.STATUS ):
    print("old_status =", old_status)
    print("old_status.value =", old_status.value)
    print("new_status =", new_status)
    print("new_status.value =", new_status.value)
    print(
        "allowed =",
        ALLOWABLE_BOOKING_STATUS_CHANGES[old_status.value]
    )
    print(
        "is allowed =",
        new_status.value in ALLOWABLE_BOOKING_STATUS_CHANGES[old_status.value]
    )

    if new_status.value in ALLOWABLE_BOOKING_STATUS_CHANGES[old_status.value]:
        return new_status

    new_status = new_status.value
    raise BookingException(f"the status {new_status} is not allowed for this booking")

@transaction.atomic
def create_booking(*, barber_id: int, service: Service, hairstyle: Hairstyle, color: Color,
                   total_price: int, session_start_date_time_in_salon_tz: datetime,
                   session_end_date_time_in_salon_tz: datetime,
                   customer_name: str, phone_number, booking_source: str, booked_by: str,
                   salon_timezone:ZoneInfo, status=Booking.STATUS.CONFIRMED ):

    if timezone.is_naive(session_start_date_time_in_salon_tz):
        raise ValueError( "session_start_date_time_salon_time must be timezone-aware." )

    if timezone.is_naive(session_end_date_time_in_salon_tz):
        raise ValueError( "session_end_date_time_salon_time must be timezone-aware." )

    # convert the start and end time to utc time
    session_start_date_time_utc = session_start_date_time_in_salon_tz.astimezone(dt_timezone.utc)
    session_end_date_time_utc = session_end_date_time_in_salon_tz.astimezone(dt_timezone.utc)
    booking_date_in_salon_tz = session_start_date_time_in_salon_tz.date()

    # Lock this barber for the duration of the transaction.
    # Any other booking attempt for this same barber must wait.
    barber = ( StaffProfile.objects.select_for_update().get(pk=barber_id) )

    BarberScheduler().validate_no_overlap(
                    barber=barber, session_start_utc=session_start_date_time_utc,
                    session_end_utc=session_end_date_time_utc,
                    salon_timezone=salon_timezone,
                )
    BarberScheduler().validate_no_overlap_with_barber_breaktime_or_off_days(
        barber=barber, session_start_utc=session_start_date_time_utc,
        session_end_utc=session_end_date_time_utc, salon_timezone=salon_timezone,
    )


    booking = Booking(service=service, hairstyle=hairstyle, color=color, barber=barber,
    booking_date=booking_date_in_salon_tz, session_start_date_time=session_start_date_time_utc,
    session_end_date_time=session_end_date_time_utc, customer_name=customer_name,
    booking_source=booking_source, phone_number=phone_number, price=total_price, booked_by=booked_by,
    status=status

    )

    # booking.full_clean()
    booking.save()
    return booking



@transaction.atomic
def update_booking( *, booking_reference:str, status:Booking.STATUS,  reason_for_cancellation=None, ):

    booking = ( Booking.objects.select_for_update().get(booking_reference=booking_reference) )

    # # Cancellation requires a reason
    # if ( status == Booking.STATUS.CANCELLED ):
    #
    #     if ( not reason_for_cancellation ):
    #         raise ValidationError({
    #             "reason_for_cancellation": "A cancellation reason is required when cancelling a booking."
    #         })
    #
    #     if (booking.status == Booking.STATUS.COMPLETED):
    #         raise ValidationError({
    #             "details": "This booking was already cancelled and cannot be completed "
    #                        "please place another service session."
    #         })
    #
    #     if ( booking.status==Booking.STATUS.CANCELLED ):
    #         raise ValidationError({
    #             "details": "This booking was already cancelled."
    #         })


    # Do not allow a cancellation reason for a non-cancelled booking
    if status != Booking.STATUS.CANCELLED:
        reason_for_cancellation = booking.reason_for_cancellation

    old_status = Booking.STATUS(booking.status)

    allowable_status_change(old_status=old_status, new_status=status)
    booking.status = status
    booking.reason_for_cancellation = reason_for_cancellation

    # Run model validation before saving
    booking.full_clean()

    booking.save( update_fields=[ "status", "reason_for_cancellation", ] )

    return booking


# this method receives data from serializer and convert fields with data as datetime
# in utc to salon timezone and make or add start_time, end_time to the dataset for
# frontend display purposes
def booking_data_with_timezone(*, data: dict | list[dict]) -> dict | list[dict]:

    salon_info = get_salon_info_config()
    salon_timezone = ZoneInfo(salon_info["time_zone"])

    if not isinstance(data, (dict, list)):
        raise ValidationError({"details": "invalid booking data. booking data "
                                          "is either a dict or a list of dict"})

    if isinstance(data, dict):
        if "booking_date" not in data:
            raise ValidationError({"details": "A booking 'date' is required."})


        if "session_start_date_time" not in data:
            raise ValidationError({"details": "A booking 'session_start_date_time' is required."})

        session_start_date_time_str = data['session_start_date_time']

        session_start_date_time = convert_utc_iso_to_salon_time(session_start_date_time_str, salon_timezone)

        if "session_end_date_time" not in data:
            raise ValidationError({"details": "A booking 'session_end_date_time' is required."})

        session_end_date_time_str = data['session_end_date_time']

        session_end_date_time = convert_utc_iso_to_salon_time(session_end_date_time_str, salon_timezone)

        data['start_time'] = session_start_date_time.time()
        data['end_time'] = session_end_date_time.time()

        return data

    elif isinstance(data, list):

        res_list: list[dict] = []

        for item in data:

            if not isinstance(item, dict):
                raise ValidationError({
                    "details": "Each item in booking data must be a dictionary."
                })

            if "booking_date" not in item:
                raise ValidationError({"details": "A booking 'date' is required."})


            if "session_start_date_time" not in item:
                raise ValidationError({"details": "A booking 'session_start_date_time' is required."})
            session_start_date_time_str = item['session_start_date_time']

            session_start_date_time = convert_utc_iso_to_salon_time(session_start_date_time_str, salon_timezone)

            if "session_end_date_time" not in item:
                raise ValidationError({"details": "A booking 'session_end_date_time' is required."})
            session_end_date_time_str = item['session_end_date_time']

            session_end_date_time = convert_utc_iso_to_salon_time(session_end_date_time_str, salon_timezone)

            item['start_time'] = session_start_date_time.time()
            item['end_time'] = session_end_date_time.time()

            res_list.append(item)

        return res_list




