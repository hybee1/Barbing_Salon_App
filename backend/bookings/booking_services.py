
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from backend.accounts.models import StaffProfile
from backend.bookings.models import Booking
from backend.salon_settings.services_salon_config import get_salon_info_config
from backend.utils.services import BarberScheduler


@transaction.atomic
def create_booking( *, barber_id: int, service_id: int, hairstyle_id: int, color_id: int,
                    total_price: int, session_start_date_time_salon_time: datetime,
                    session_end_date_time_salon_time: datetime,
                    customer_name: str, phone_number, booking_source: str, booked_by: str,
                    salon_timezone:ZoneInfo):

    if timezone.is_naive( session_start_date_time_salon_time ):
        raise ValueError( "session_start_date_time_salon_time must be timezone-aware." )

    if timezone.is_naive( session_end_date_time_salon_time ):
        raise ValueError( "session_end_date_time_salon_time must be timezone-aware." )

    # convert the start and end time to utc time
    session_start_date_time_utc = session_start_date_time_salon_time.astimezone(timezone.utc)
    session_end_date_time_utc = session_end_date_time_salon_time.astimezone(timezone.utc)
    booking_date = session_start_date_time_salon_time.date()

    # Lock this barber for the duration of the transaction.
    # Any other booking attempt for this same barber must wait.
    barber = ( StaffProfile.objects.select_for_update().get(pk=barber_id) )

    BarberScheduler().validate_no_overlap(
                    barber=barber, booking_date_in_salon_tz=booking_date,
                    session_start_utc=session_start_date_time_utc, session_end_utc=session_end_date_time_utc,
                    salon_timezone=salon_timezone,
                )
    BarberScheduler().validate_no_overlap_with_barber_breaktime_or_off_days(
        barber=barber, session_start_utc=session_start_date_time_utc,
        session_end_utc=session_end_date_time_utc, salon_timezone=salon_timezone,
    )


    booking = Booking(

    booking_reference=None, service=service_id, hairstyle=hairstyle_id, color=color_id,
    barber=barber, booking_date=booking_date, session_start_date_time=session_start_date_time_utc,
    session_end_date_time=session_end_date_time_utc, customer_name=customer_name,
    booking_source=booking_source, phone_number=phone_number, price=total_price, booked_by=booked_by

    )

    booking.full_clean()
    booking.save()
    return booking



@transaction.atomic
def update_booking( *, booking_reference, status,  reason_for_cancellation=None, ):

    booking = ( Booking.objects.select_for_update().get(booking_reference=booking_reference) )

    # Cancellation requires a reason
    if ( status == Booking.STATUS.CANCELLED ):

        if ( not reason_for_cancellation ):
            raise ValidationError({
                "reason_for_cancellation": "A cancellation reason is required when cancelling a booking."
            })

        if (booking.status == Booking.STATUS.COMPLETED):
            raise ValidationError({
                "details": "This booking was already cancelled and cannot be completed "
                           "please place another service session."
            })

        if ( booking.status==Booking.STATUS.CANCELLED ):
            raise ValidationError({
                "details": "This booking was already cancelled."
            })



    # Do not allow a cancellation reason for a non-cancelled booking
    if status != Booking.STATUS.CANCELLED:
        reason_for_cancellation = booking.reason_for_cancellation

    booking.status = status
    booking.reason_for_cancellation = reason_for_cancellation

    # Run model validation before saving
    booking.full_clean()

    booking.save( update_fields=[ "status", "reason_for_cancellation", ] )

    return booking


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

        if "session_end_date_time" not in data:
            raise ValidationError({"details": "A booking 'session_end_date_time' is required."})
        session_end_date_time_str = data['session_end_date_time']

        # booking_date_start_time_str = f"{booking_date_str} {start_time_str}"
        # booking_date_end_time_str = f"{booking_date_str} {end_time_str}"

        # booking_date_start_time = datetime.strptime(booking_date_start_time_str, "%Y-%m-%d %H:%M")
        # booking_date_end_time = datetime.strptime(booking_date_end_time_str, "%Y-%m-%d %H:%M")

        booking_date_start_time = session_start_date_time_str.astimezone(salon_timezone)
        booking_date_end_time = session_end_date_time_str.astimezone(salon_timezone)

        data['start_time'] = booking_date_start_time.time()
        data['end_time'] = booking_date_end_time.time()

        return data

    elif isinstance(data, list):

        res_list: list[dict] = []
        for item in data:
            if "booking_date" not in item:
                raise ValidationError({"details": "A booking 'date' is required."})
            booking_date_str = item['booking_date']

            if "session_start_date_time" not in item:
                raise ValidationError({"details": "A booking 'session_start_date_time' is required."})
            session_start_date_time_str = item['session_start_date_time']

            if "session_end_date_time" not in item:
                raise ValidationError({"details": "A booking 'session_end_date_time' is required."})
            session_end_date_time_str = item['session_end_date_time']

            # booking_date_start_time_str = f"{booking_date_str} {start_time_str}"
            # booking_date_end_time_str = f"{booking_date_str} {end_time_str}"
            #
            # booking_date_start_time = datetime.strptime(booking_date_start_time_str, "%Y-%m-%d %H:%M")
            # booking_date_end_time = datetime.strptime(booking_date_end_time_str, "%Y-%m-%d %H:%M")

            booking_date_start_time = session_start_date_time_str.astimezone(salon_timezone)
            booking_date_end_time = session_end_date_time_str.astimezone(salon_timezone)

            item['start_time'] = booking_date_start_time.time()
            item['end_time'] = booking_date_end_time.time()

            res_list.append(item)

        return res_list




