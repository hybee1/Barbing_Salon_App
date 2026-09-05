from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.accounts.models import StaffProfile
from backend.bookings.models import Booking
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.custom_permissions.permissions import Is_Authenticated_Staff_User


class SalonManagerDashboardStatsView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        timezome_date_time = timezone.localtime()

        date_today = timezome_date_time.date()
        current_time = timezome_date_time.time()

        today_bookings_count = Booking.objects.filter( booking_date=date_today).count()

        completed_bookings_today_count = Booking.objects.filter(
                    booking_date=date_today, status__iexact='COMPLETED').count()

        active_staffs = (
            StaffProfile.objects.filter(
                status=StaffProfile.StaffStatus.ACTIVE,
            )
            .exclude(
                breaktime_or_off_days__date=date_today,
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
            date=date_today, start_time__lte=current_time, end_time__gte=current_time
        ).count()

        data = {
            "username": request.user.username,
            "today_bookings_count": today_bookings_count,
            "completed_bookings_today": completed_bookings_today_count,
            "active_staffs_count": active_staffs_count,
            "active_break_count": active_break_count
            }

        return Response(data, status=status.HTTP_200_OK)
