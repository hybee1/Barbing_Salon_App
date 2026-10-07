from django.db.models import Q
from datetime import timezone as dt_timezone
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.accounts.models import StaffProfile
from backend.bookings.models import Booking
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.custom_permissions.permissions import Is_Authenticated_Staff_User, Is_SalonManager


class SalonManagerDashboardStatsView(APIView):

    permission_classes = [Is_SalonManager]

    def get(self, request):

        now_date_time_in_salon_tz = timezone.localtime()

        date_today_in_salon_tz = now_date_time_in_salon_tz.date()
        current_time_in_salon_tz = now_date_time_in_salon_tz.time()

        today_bookings_count = Booking.objects.filter( booking_date=date_today_in_salon_tz).count()

        completed_bookings_today_count = Booking.objects.filter(
                    booking_date=date_today_in_salon_tz, status=Booking.STATUS.COMPLETED).count()

        breaktime_or_off_days__date_utc = now_date_time_in_salon_tz.astimezone(dt_timezone.utc)

        active_staffs = (
            StaffProfile.objects.filter(
                status=StaffProfile.StaffStatus.ACTIVE,
            )
            .exclude(
                Q(breaktime_or_off_days__break_date=date_today_in_salon_tz) |
                Q(breaktime_or_off_days__break_start_date_time__range=(breaktime_or_off_days__date_utc,
                                                                       breaktime_or_off_days__date_utc)),
                breaktime_or_off_days__status__in=[
                    BreakTimeAndOffDays.BlockStatus.OFF_DAY,
                    BreakTimeAndOffDays.BlockStatus.ON_LEAVE,
                    BreakTimeAndOffDays.BlockStatus.SICK_LEAVE,
                    BreakTimeAndOffDays.BlockStatus.PERSONAL,
                    BreakTimeAndOffDays.BlockStatus.OTHER,
                ],
            )
        )

        active_staffs_count = active_staffs.count()

        active_break_count = BreakTimeAndOffDays.objects.filter(
            staff__status=StaffProfile.StaffStatus.ACTIVE,
            status=BreakTimeAndOffDays.BlockStatus.BREAK,
            # break_date=date_today_in_salon_tz,
            break_start_date_time__lte=breaktime_or_off_days__date_utc,
            break_end_date_time__gte=breaktime_or_off_days__date_utc
        ).count()

        data = {
            "username": request.user.username,
            "today_bookings_count": today_bookings_count,
            "completed_bookings_today": completed_bookings_today_count,
            "active_staffs_count": active_staffs_count,
            "active_break_count": active_break_count
            }

        return Response(data, status=status.HTTP_200_OK)
