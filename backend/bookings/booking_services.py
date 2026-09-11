from django.core.exceptions import ValidationError
from django.db import transaction

from backend.accounts.models import StaffProfile
from backend.bookings.models import Booking


@transaction.atomic
def create_booking( *, barber_id, service_id, hairstyle_id, color_id, total_price,
                       booking_date, start_time, end_time, customer_name, phone_number,
                    booking_source, booked_by, ):

    # Lock this barber for the duration of the transaction.
    # Any other booking attempt for this same barber must wait.
    barber = ( StaffProfile.objects.select_for_update().get(pk=barber_id) )


    booking = Booking(

    booking_reference=None, service=service_id, hairstyle=hairstyle_id, color=color_id,
    barber=barber, booking_date=booking_date, start_time=start_time, end_time=end_time,
    customer_name=customer_name, booking_source=booking_source, phone_number=phone_number,
    price=total_price, booked_by=booked_by

    )

    booking.full_clean()
    booking.save()
    return booking



@transaction.atomic
def update_booking( *, booking_reference, status,  reason_for_cancellation=None, ):

    booking = ( Booking.objects.select_for_update().get(booking_reference=booking_reference) )

    # Cancellation requires a reason
    if ( status == Booking.STATUS.CANCELLED and not reason_for_cancellation ):
        raise ValidationError({
            "reason_for_cancellation": "A cancellation reason is required when cancelling a booking."
        })

    # Do not allow a cancellation reason for a non-cancelled booking
    if status != Booking.STATUS.CANCELLED:
        reason_for_cancellation = None

    booking.status = status
    booking.reason_for_cancellation = reason_for_cancellation

    # Run model validation before saving
    booking.full_clean()

    booking.save( update_fields=[ "status", "reason_for_cancellation", ] )

    return booking
