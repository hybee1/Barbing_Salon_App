from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import transaction

from backend.accounts.models import StaffProfile
from backend.bookings.models import Booking
from backend.salon_settings.services_salon_config import get_salon_info_config


@transaction.atomic
def create_booking( *, barber_id, service_id, hairstyle_id, color_id, total_price,
                       booking_date, session_start_date_time, session_end_date_time,
                    customer_name, phone_number, booking_source, booked_by, ):

    # convert the start and end time to utc time
    session_start_date_time_utc = session_start_date_time.astimezone(timezone.utc).time()
    session_end_date_time_utc = session_end_date_time.astimezone(timezone.utc).time()

    # Lock this barber for the duration of the transaction.
    # Any other booking attempt for this same barber must wait.
    barber = ( StaffProfile.objects.select_for_update().get(pk=barber_id) )


    booking = Booking(

    booking_reference=None, service=service_id, hairstyle=hairstyle_id, color=color_id,
    barber=barber, booking_date=booking_date, session_start_date_time=session_start_date_time_utc,
    session_end_date_time_utc=session_end_date_time_utc, customer_name=customer_name,
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


def booking_data_with_timezone(*, data: dict | list[dict]) -> dict |list[dict]:
    salon_info = get_salon_info_config()
    salon_timezone = salon_info.timezone

    if not isinstance(data, (dict, list)):
        raise ValidationError({"details": "invalid booking data. booking data "
                                          "is either a dict or a list of dict"})

    if isinstance(data, dict):
        if "booking_date" not in data:
            raise ValidationError({"details": "A booking 'date' is required."})
        booking_date_str = data['booking_date']

        if "start_time" not in data:
            raise ValidationError({"details": "A booking 'start_time' is required."})
        start_time_str = data['start_time']

        if "end_time" not in data:
            raise ValidationError({"details": "A booking 'end_time' is required."})
        end_time_str = data['end_time']

        booking_date_start_time_str = f"{booking_date_str} {start_time_str}"
        booking_date_end_time_str = f"{booking_date_str} {end_time_str}"

        booking_date_start_time = datetime.strptime(booking_date_start_time_str, "%Y-%m-%d %H:%M")
        booking_date_end_time = datetime.strptime(booking_date_end_time_str, "%Y-%m-%d %H:%M")

        booking_date_start_time = booking_date_start_time.replace(tzinfo=timezone.utc).astimezone(salon_timezone)
        booking_date_end_time = booking_date_end_time.replace(tzinfo=timezone.utc).astimezone(salon_timezone)

        data['start_time'] = booking_date_start_time.time()
        data['end_time'] = booking_date_end_time.time()

        return data

    elif isinstance(data, list):

        res_list: list[dict] = []
        for item in data:
            if "booking_date" not in item:
                raise ValidationError({"details": "A booking 'date' is required."})
            booking_date_str = item['booking_date']

            if "start_time" not in item:
                raise ValidationError({"details": "A booking 'start_time' is required."})
            start_time_str = item['start_time']

            if "end_time" not in item:
                raise ValidationError({"details": "A booking 'end_time' is required."})
            end_time_str = item['end_time']

            booking_date_start_time_str = f"{booking_date_str} {start_time_str}"
            booking_date_end_time_str = f"{booking_date_str} {end_time_str}"

            booking_date_start_time = datetime.strptime(booking_date_start_time_str, "%Y-%m-%d %H:%M")
            booking_date_end_time = datetime.strptime(booking_date_end_time_str, "%Y-%m-%d %H:%M")

            booking_date_start_time = booking_date_start_time.astimezone(salon_timezone)
            booking_date_end_time = booking_date_end_time.astimezone(salon_timezone)

            item['start_time'] = booking_date_start_time.time()
            item['end_time'] = booking_date_end_time.time()

            res_list.append(item)

        return res_list

