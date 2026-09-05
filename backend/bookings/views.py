from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.bookings.models import Booking
from backend.bookings.serializers import (BookingSerializer, BarberAvailableTimeQuerySerializer,
                                          BookingReadSerializer, BarberBookingStatsSerializer,
                                          BarberBookingsTodaySerializer)
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.custom_permissions.permissions import Is_Authenticated_Staff_User, Is_SalonManager, Is_Barber, Is_Stylist, \
    Is_Barber_Stylist, Is_Receptionist
from backend.exceptions.exceptions import BookingDateException
from backend.services.models import Service, Hairstyle, Color
from backend.utils.services import BarberScheduler


class BookingView(APIView):

    permission_classes = [Is_SalonManager, Is_Barber, Is_Receptionist, Is_Stylist, Is_Barber_Stylist]

    def get(self, request):

        bookings = Booking.objects.all()

        booking_id = request.query_params.get("booking_id")

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        staff = request.query_params.get("staff")
        status = request.query_params.get("status")

        # booking id
        if booking_id:
            bookings = bookings.filter(id=booking_id)

        if start_date and end_date:

            if(end_date < start_date):
                raise BookingDateException(end_date)

            # Date range filter
            if start_date:

                start_date = parse_date(start_date)

                if start_date:
                    bookings = bookings.filter( booking_date__gte=start_date )

            if end_date:

                end_date = parse_date(end_date)

                if end_date:
                    bookings = bookings.filter( booking_date__lte=end_date )

        # Staff filter
        if staff:
            bookings = bookings.filter( staff_id=staff )

        # Status filter
        if status and status.upper() != "ALL STATUS":
            bookings = bookings.filter( status=status )

        bookings = bookings.order_by( "-booking_date", "-start_time" )

        serializer = BookingReadSerializer( bookings, many=True )

        return Response(serializer.data)


class CreateBookingView(APIView):

    def post(self, request):


        service_id = (request.data.get("service") or {}).get("id", None)

        service = None
        service_price = 0
        service_duration_minutes = 0
        if service_id is not None:
            service = get_object_or_404(
                Service.objects.only("price", "duration_minutes"), id=service_id,
            )
            service_price = service.price
            service_duration_minutes = service.duration_minutes

        hairstyle_id = (request.data.get("hairstyle") or {}).get("id", None)

        hairstyle = None
        hairstyle_price = 0
        hairstyle_duration_minutes = 0
        if hairstyle_id is not None:
            hairstyle = get_object_or_404(
                Hairstyle.objects.only("price", "duration_minutes"), id=hairstyle_id,
            )
            hairstyle_price = hairstyle.price
            hairstyle_duration_minutes = hairstyle.duration_minutes

        barber_id = (request.data.get("barber") or {}).get("id", None)

        color_id = (request.data.get("color") or {}).get("id", None)
        color = None
        color_price = 0
        color_duration_minutes = 0
        if color_id is not None:
            color = get_object_or_404(
                Color.objects.only("price", "duration_minutes"), id=color_id,
            )
            color_price = color.price
            color_duration_minutes = color.duration_minutes

        booking_date = request.data.get("date")

        start_time_str = request.data.get("time")

        datetime_str = f"{booking_date} {start_time_str}"

        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                start_datetime = datetime.strptime(datetime_str, fmt)
                break
            except ValueError:
                pass
        else:
            raise ValidationError({ "time": "Invalid date/time format." })

        total_duration = timedelta(
            minutes=service_duration_minutes + hairstyle_duration_minutes + color_duration_minutes
        )

        end_datetime = start_datetime + total_duration

        start_time = start_datetime.time()

        end_time = end_datetime.time()

        customer = request.data.get("customer") or {}

        customer_name = customer.get("customer_name") or None

        phone_number = customer.get("phone")

        total_price = service_price + hairstyle_price + color_price

        booked_by = request.data.get("booked_by") or "Customer"

        serializer = BookingSerializer(data = {

            "service": service_id, "hairstyle": hairstyle_id, "color": color_id,
            "barber": barber_id, "booking_date": booking_date, "start_time": start_time,
            "end_time": end_time, "customer_name": customer_name,
            "phone_number": phone_number, "price": total_price, "booked_by": booked_by

        })

        serializer.is_valid(raise_exception=True)

        barber_scheduler = BarberScheduler()

        barber_scheduler.is_overlap(
                                   serializer.validated_data['barber'],
                                   serializer.validated_data['booking_date'],
                                   serializer.validated_data['start_time'],
                                   serializer.validated_data['end_time'])

        with transaction.atomic():
            confirmed_booking = serializer.save()

        return Response({
            "message": "Booking created successfully.",
            "booking_reference": confirmed_booking.booking_reference},
            status=status.HTTP_201_CREATED)


class TodayBooking_Api_View(APIView):

    permission_classes = [Is_SalonManager]

    def get(self, request):

        today_date = timezone.localdate()
        bookings_for_today = Booking.objects.filter(booking_date=today_date)

        serializer = BookingReadSerializer( bookings_for_today, many=True )

        return Response(serializer.data)


class BookingForLast7Days_Api_View(APIView):

    permission_classes = [Is_SalonManager, Is_Barber, Is_Stylist, Is_Barber_Stylist]

    def get(self, request):

        today_date = timezone.localdate()
        last_7_days = today_date - timedelta(days=7)

        booking_obj = (Booking.objects.filter(
            booking_date__range=(last_7_days, today_date)
        ).order_by("booking_date", "-start_time"))

        serializer = BookingReadSerializer(booking_obj, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberBookingAvailability_Api_View(APIView):

    #  for customers to see available barbers

    def get(self, request):

        serializer = BarberAvailableTimeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        barber_id = serializer.validated_data["barber_id"]

        date1 = serializer.validated_data["date"]

        total_service_duration = serializer.validated_data["total_service_duration"]

        barber_scheduler = BarberScheduler()

        available_start_time = barber_scheduler.check_schedule(
                                                 barber_id, date1, total_service_duration)

        return Response(available_start_time, status=status.HTTP_200_OK)


class BarberBookingStatsView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]


    def get(self, request):

        barber = request.user.staffprofile



        date_today = timezone.localdate()

        barber_bookings_stats_for_today = Booking.objects.filter(
                                                    booking_date=date_today, barber=barber)

        barber_total_bookings_for_today = barber_bookings_stats_for_today.count()

        completed = 0
        upcoming = 0
        for stat in barber_bookings_stats_for_today:

            if (Booking.STATUS(stat.status) == Booking.STATUS.COMPLETED):

                completed += 1

            if (stat.start_time >= timezone.localtime().time() and
                    Booking.STATUS(stat.status) in [Booking.STATUS.ARRIVED,
                                                    Booking.STATUS.CONFIRMED]):

                upcoming += 1

        date_now = timezone.localdate()

        break_or_off_days = (BreakTimeAndOffDays.objects.filter(
            staff=barber, date=date_now)[0:7])


        time_now = timezone.localtime().time()

        if (break_or_off_days.count() == 0):

            break_status = BreakTimeAndOffDays.BlockStatus.AVAILABLE.label

        if ( break_or_off_days.count() > 0):
            for break_stat in break_or_off_days:

                if ( break_stat.start_time < time_now and
                                            break_or_off_days.end_time > time_now ):

                    break_status = break_stat.status.label

                else:
                    break_status = BreakTimeAndOffDays.BlockStatus.AVAILABLE.label

        serializer = BarberBookingStatsSerializer({
                                        "today_count": barber_total_bookings_for_today,
                                        "completed_count": completed,
                                        "upcoming_count": upcoming,
                                        "break_status": break_status
                                    })

        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberBookingsToday(APIView):

    permission_classes = [Is_SalonManager, Is_Barber, Is_Receptionist, Is_Stylist, Is_Barber_Stylist]

    def get(self, request):

        barber = request.user.staffprofile

        date_today = timezone.localdate()

        barber_bookings_stats_for_today = Booking.objects.filter(
                            booking_date=date_today, barber=barber,
                            status=Booking.STATUS.CONFIRMED)

        serializer = BarberBookingsTodaySerializer(barber_bookings_stats_for_today, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberUpcomingBookingsToday(APIView):

    permission_classes = [Is_SalonManager, Is_Barber, Is_Stylist, Is_Barber_Stylist]

    def get(self, request):

        barber = request.user.staffprofile

        date_and_time = timezone.localtime()
        date_today = date_and_time.date()
        current_time = date_and_time.time()

        barber_bookings_stats_for_today = Booking.objects.filter(
                            booking_date=date_today, barber=barber,
                            start_time__gte=current_time,
                            status=Booking.STATUS.CONFIRMED)

        serializer = BarberBookingsTodaySerializer(barber_bookings_stats_for_today, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


