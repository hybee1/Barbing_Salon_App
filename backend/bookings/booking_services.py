from datetime import datetime, timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from backend.accounts.models import User, StaffProfile
from backend.bookings.serializers import BookingSerializer
from backend.services.models import Service, Hairstyle, Color
from backend.utils.services import BarberScheduler


class BookingService:

    @staticmethod
    def create_booking( *, customer_data, barber_id=None, service_id=None, hairstyle_id=None, color_id=None,
                           booking_date, start_time_str, booking_source, booked_by, ):

        # get service using service_id
        service = None
        service_price = 0
        service_duration_minutes = 0
        if service_id is not None:
            service = get_object_or_404(
                Service.objects.only("price", "duration_minutes"), id=service_id,
            )
            #  validate if service is active
            if not service.is_active:
                raise ValidationError({
                    "service": "This Service is temporarily unavailable, please select another Service."
                })

            service_price = service.price
            service_duration_minutes = service.duration_minutes

        # get hairstyle using hairstyle_id
        hairstyle_price = 0
        hairstyle_duration_minutes = 0
        if hairstyle_id is not None:

            if service is None:
                raise ValidationError({
                    "service": "Service is required when selecting a hairstyle."
                })

            hairstyle = get_object_or_404(
                Hairstyle.objects.only("price", "duration_minutes"), id=hairstyle_id,
            )

            #  validate if hairstyle belongs to that service
            if hairstyle and hairstyle.service_id != service.id:
                raise ValidationError({
                    "hairstyle": "Hairstyle does not belong to the selected service."
                })

            #  validate if hairstyle is active
            if not hairstyle.is_active:
                raise ValidationError({
                    "hairstyle": "This Hairstyle is temporarily unavailable, please select another Hairstyle."
                })

            hairstyle_price = hairstyle.price
            hairstyle_duration_minutes = hairstyle.duration_minutes


        # get color using color_id
        color_price = 0
        color_duration_minutes = 0
        if color_id is not None:

            if service is None:
                raise ValidationError({
                    "service": "Service is required when selecting a color."
                })

            color = get_object_or_404(
                Color.objects.only("price", "duration_minutes"), id=color_id,
            )

            #  validate if color belongs to that service
            if color and color.service_id != service.id:
                raise ValidationError({
                    "color": "Color does not belong to the selected service."
                })

            #  validate if color is active
            if not color.is_active:
                raise ValidationError({
                    "color": "This Color is temporarily unavailable, please select another Color."
                })

            color_price = color.price
            color_duration_minutes = color.duration_minutes

        datetime_str = f"{booking_date} {start_time_str}"

        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                start_datetime = datetime.strptime(datetime_str, fmt)
                break
            except ValueError:
                pass
        else:
            raise ValidationError({"time": "Invalid date/time format."})

        total_duration = timedelta(
            minutes=service_duration_minutes + hairstyle_duration_minutes + color_duration_minutes
        )

        end_datetime = start_datetime + total_duration

        start_time = start_datetime.time()

        end_time = end_datetime.time()

        customer_name = customer_data.get("customer_name") or None

        phone_number = customer_data.get("phone")

        total_price = service_price + hairstyle_price + color_price

        serializer = BookingSerializer(data={

            "service": service_id, "hairstyle": hairstyle_id, "color": color_id,
            "barber": barber_id, "booking_date": booking_date, "start_time": start_time,
            "end_time": end_time, "customer_name": customer_name, "booking_source": booking_source,
            "phone_number": phone_number, "price": total_price, "booked_by": booked_by

        })

        serializer.is_valid(raise_exception=True)

        barber_scheduler = BarberScheduler()

        with transaction.atomic():
            barber = (
                StaffProfile.objects
                .select_for_update()
                .get(pk=serializer.validated_data["barber"].pk)
            )

            barber_scheduler.is_overlap(
                barber,
                serializer.validated_data['booking_date'],
                serializer.validated_data['start_time'],
                serializer.validated_data['end_time'])

            return serializer.save()
