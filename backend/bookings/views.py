
from datetime import timedelta, datetime

from django.db.models import Count, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.bookings.models import Booking
from backend.bookings.serializers import (BarberAvailableTimeQuerySerializer,
                                          BookingReadSerializer, BarberBookingStatsSerializer,
                                          BarberBookingsTodaySerializer, BookingSerializer, CreateBookingSerializer,
                                          UpdateBookingSerializer)
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.custom_permissions.permissions import (Is_Authenticated_Staff_User, Is_SalonManager,
                                                    SalonManager_Or_Barber_Or_Stylist_Or_Is_Barber_Stylist,
                                                    SalonManager_Or_Receptionist,
                                                    SalonManager_Or_Barber_Or_Stylist_Or_Is_Barber_Stylist_Or_Receptionist)
from backend.exceptions.exceptions import BookingDateException
from backend.rate_limit_or_throttling.booking_create_throttle import BookingCreateThrottle
from backend.utils.services import BarberScheduler


class ManageBooking_Api_View(APIView):

    def get_throttles(self):
        if self.request.method == "POST":
            throttle_classes = [BookingCreateThrottle]

        else:
            throttle_classes = []

        return [throttle() for throttle in throttle_classes]

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [Is_SalonManager]

        elif self.request.method == "POST":
            permission_classes = [ AllowAny, ]

        elif self.request.method == "DELETE":
            permission_classes = [Is_SalonManager, ]

        else:
            permission_classes = [ SalonManager_Or_Barber_Or_Stylist_Or_Is_Barber_Stylist_Or_Receptionist, ]

        return [permission() for permission in permission_classes]

    def get(self, request):

        bookings = ( Booking.objects.select_related( "barber__user", "service", "hairstyle", "color", )
                   )

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

    def patch(self, request, booking_reference):

        try:
            booking = Booking.objects.get( booking_reference=booking_reference )

        except Booking.DoesNotExist:
            return Response(
                { "detail": "Booking not found." }, status=status.HTTP_404_NOT_FOUND )

        serializer = UpdateBookingSerializer( booking, data=request.data, partial=True )

        serializer.is_valid( raise_exception=True )

        booking = serializer.save()

        return Response( BookingReadSerializer(booking).data, status=status.HTTP_200_OK )


class CreateBookingView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [BookingCreateThrottle]

    def post(self, request):

        # means the customer walked-in and a staff (reception, barber..) help booked a barbing session
        # for the customer or the staff his/her self booked a barbing session for their self
        user = request.user

        if user.is_authenticated and user.is_staff :
            booking_source = Booking.BookingSource.WALK_IN
            booked_by = user.username
        else:
            booking_source = Booking.BookingSource.ONLINE
            booked_by = "Customer"

        service_id: dict | None  = (request.data.get("service") or {}).get("id", None)

        hairstyle_id: dict | None = (request.data.get("hairstyle") or {}).get("id", None)

        barber_id = (request.data.get("barber") or {}).get("id", None)

        color_id: dict | None = (request.data.get("color") or {}).get("id", None)

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
            raise ValidationError({"time": "Invalid date/time format."})

        start_time = start_datetime.time()

        customer_data = request.data.get("customer") or {}

        customer_name = customer_data.get("customer_name") or None

        phone_number = customer_data.get("phone")

        serializer = CreateBookingSerializer(data={

            "service": service_id, "hairstyle": hairstyle_id, "color": color_id,
            "barber": barber_id, "booking_date": booking_date, "start_time": start_time,
             "customer_name": customer_name, "booking_source": booking_source,
            "phone_number": phone_number, "booked_by": booked_by

        })

        serializer.is_valid(raise_exception=True)

        confirmed_booking = serializer.save()

        # confirmed_booking = BookingService().create_booking(
        #     customer_data=customer_data, barber_id=barber_id, service_id=service_id,
        #     hairstyle_id=hairstyle_id, color_id=color_id, booking_date=booking_date,
        #     start_time_str=start_time_str, booking_source=booking_source, booked_by=booked_by
        # )

        return Response({
            "message": "Booking created successfully.",
            "booking_reference": confirmed_booking.booking_reference},
            status=status.HTTP_201_CREATED)


class TodayBooking_Api_View(APIView):

    permission_classes = [Is_SalonManager]

    def get(self, request):

        today_date = timezone.localdate()
        bookings_for_today = (
            Booking.objects.select_related( "barber__user", "service","hairstyle", "color",
                        ).filter( booking_date=today_date )
        )

        serializer = BookingReadSerializer( bookings_for_today, many=True )

        return Response(serializer.data)


class OneBarberBookingForLast7Days_Api_View(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        today_date = timezone.localdate()
        last_7_days = today_date - timedelta(days=7)

        if not BarberScheduler().can_receive_bookings(request.user.staffprofile):
            return Response(
                {"detail": "Access Denied."}, status=status.HTTP_403_FORBIDDEN,
            )

        booking_obj = (
                        Booking.objects.select_related(
                            "barber__user", "service", "hairstyle", "color",
                        ).filter(
                                barber=request.user.staffprofile,
                                booking_date__range=(last_7_days, today_date),
                        ).order_by("booking_date", "-start_time")
        )

        serializer = BookingReadSerializer(booking_obj, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingForLast7Days_Api_View(APIView):

    permission_classes = [SalonManager_Or_Receptionist]

    def get(self, request):

        today_date = timezone.localdate()
        last_7_days = today_date - timedelta(days=7)

        booking_obj = ( Booking.objects .select_related(
                        "barber__user",
                        "service",
                        "hairstyle",
                        "color",
                    ).filter(
                        booking_date__range=(last_7_days, today_date),
                    )
                    .order_by("booking_date", "-start_time")
        )

        serializer = BookingReadSerializer(booking_obj, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberBookingAvailability_Api_View(APIView):
    throttle_classes = [BookingCreateThrottle]

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

    permission_classes = [Is_Authenticated_Staff_User,]

    def get(self, request):

        barber = request.user.staffprofile

        date_time_today = timezone.localtime()
        date_today = date_time_today.date()
        time_now = date_time_today.time()

        barber_bookings_stats_for_today = Booking.objects.filter(booking_date=date_today, barber=barber)

        stats = barber_bookings_stats_for_today.aggregate(
            today_count=Count("id"),
            completed_count=Count( "id",  filter=Q(status=Booking.STATUS.COMPLETED), ),
            upcoming_count=Count(
                                "id",
                                filter=Q(
                                    start_time__gte=time_now,
                                    status__in=[ Booking.STATUS.ARRIVED, Booking.STATUS.CONFIRMED, ], ),
                                ),
        )

        break_or_off_days = list( BreakTimeAndOffDays.objects.filter( staff=barber, date=date_today,)[:7] )

        if not break_or_off_days:
            break_status = ( BreakTimeAndOffDays.BlockStatus.AVAILABLE.label )
        else:
            break_status = ( BreakTimeAndOffDays.BlockStatus.AVAILABLE.label )

            for break_stat in break_or_off_days:
                if ( break_stat.start_time < time_now and break_stat.end_time > time_now ):
                    break_status = break_stat.status.label
                    break

        serializer = BarberBookingStatsSerializer({
                                        "today_count": stats.today_count,
                                        "completed_count": stats.completed_count,
                                        "upcoming_count": stats.upcoming_count,
                                        "break_status": break_status
                                    })

        return Response(serializer.data, status=status.HTTP_200_OK)


class OneBarberBookingsToday(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        barber = request.user.staffprofile

        date_today = timezone.localdate()

        if not BarberScheduler().can_receive_bookings(request.user.staffprofile):
            return Response(
                {"detail": "Access Denied."}, status=status.HTTP_403_FORBIDDEN,
            )

        barber_bookings_stats_for_today = Booking.objects.filter(
                            booking_date=date_today, barber=barber,
                            status=Booking.STATUS.CONFIRMED)

        serializer = BarberBookingsTodaySerializer(barber_bookings_stats_for_today, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class OneBarberUpcomingBookingsToday(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        barber = request.user.staffprofile

        date_and_time = timezone.localtime()
        date_today = date_and_time.date()
        current_time = date_and_time.time()

        if not BarberScheduler().can_receive_bookings(request.user.staffprofile):
            return Response(
                {"detail": "Access Denied."}, status=status.HTTP_403_FORBIDDEN,
            )

        barber_bookings_stats_for_today = ( Booking.objects
                                                        .select_related( "service", "hairstyle", )
                                                        .filter( booking_date=date_today, barber=barber,
                                                                status=Booking.STATUS.CONFIRMED,
                                                         )
                                           )

        serializer = BarberBookingsTodaySerializer(barber_bookings_stats_for_today, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberUpcomingBookingsToday(APIView):

    permission_classes = [SalonManager_Or_Barber_Or_Stylist_Or_Is_Barber_Stylist]

    def get(self, request):

        barber = request.user.staffprofile

        date_and_time = timezone.localtime()
        date_today = date_and_time.date()
        current_time = date_and_time.time()

        barber_bookings_stats_for_today = (
                                            Booking.objects.select_related(
                                                        "barber__user", "service", "hairstyle",
                                                    )
                                                    .filter(
                                                        booking_date=date_today,
                                                        start_time__gte=current_time,
                                                        status=Booking.STATUS.CONFIRMED,
                                                    )
                                            )

        serializer = BarberBookingsTodaySerializer(barber_bookings_stats_for_today, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


