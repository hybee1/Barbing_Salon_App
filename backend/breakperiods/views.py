
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from backend.breakperiods.break_periods_services import break_time_and_offDays_data_with_timezone
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.breakperiods.serializers import (BarberBreakTimeAndOffDaySerializer,
                                              BreakTimeAndOffDaysSerializer,
                                                ActiveBreakTimeSerializer)
from backend.custom_permissions.permissions import Is_Authenticated_Staff_User, Is_SalonManager
from backend.salon_settings import services_salon_config


class CreateBarberBreakTimeAndOffDayAPIView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated

    def post(self, request):
        data = request.data
        data['staff'] = request.user.staffprofile.pk

        break_date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        # for the below we considered the both are salon timezone
        break_start_date_time: datetime = datetime.fromisoformat(f"{break_date}T{start_time}")
        break_end_date_time: datetime = datetime.fromisoformat(f"{break_date}T{end_time}")

        data['break_start_date_time'] = break_start_date_time
        data['break_end_date_time'] = break_end_date_time

        serializer = BreakTimeAndOffDaysSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response("successful", status=status.HTTP_200_OK)


class Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView(APIView):
    permission_classes = [Is_SalonManager]  # only salon manager

    def get(self, request):

        salon_info = services_salon_config.get_salon_info_config()
        salon_tz = ZoneInfo(salon_info["timezone"])

        today_date_time_in_salon_tz = timezone.localtime().astimezone(salon_tz)
        today_date_in_salon_tz = today_date_time_in_salon_tz.date()

        three_days_ahead_in_salon_tz = today_date_in_salon_tz + timedelta(days=3)
        seven_days_ago_in_salon_tz = today_date_in_salon_tz - timedelta(days=7)

        break_or_off = BreakTimeAndOffDays.objects.filter(
                        break_date__range=(seven_days_ago_in_salon_tz, three_days_ahead_in_salon_tz))

        serializer = BreakTimeAndOffDaysSerializer(break_or_off, many=True)

        res = break_time_and_offDays_data_with_timezone(data=serializer.data)

        return Response(res, status=status.HTTP_200_OK)


class ActiveBreakTimeAndOffDayAPIView(APIView):
    permission_classes = [Is_SalonManager] # only salon manager

    def get(self, request):
        today_date_time_utc = timezone.localtime()

        salon_info = services_salon_config.get_salon_info_config()
        salon_tz = ZoneInfo(salon_info["timezone"])

        today_date_time_in_salon_tz = timezone.localtime().astimezone(salon_tz)
        today_date_in_salon_tz = today_date_time_in_salon_tz.date()

        active_break = BreakTimeAndOffDays.objects.filter( break_date=today_date_in_salon_tz,
                               break_start_date_time__lte=today_date_time_utc,
                               break_end_date_time__gte=today_date_time_utc )

        serializer = ActiveBreakTimeSerializer(active_break, many=True)

        res = break_time_and_offDays_data_with_timezone(data=serializer.data)

        return Response(res, status=status.HTTP_200_OK)


class OneBarberBreakTimeAndOffDayAPIView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated

    #  this return between seven days ago and three days ahead for that barber
    def get(self, request):

        salon_info = services_salon_config.get_salon_info_config()
        salon_tz = ZoneInfo(salon_info["timezone"])

        today_date_time_in_salon_tz = timezone.localtime().astimezone(salon_tz)
        today_date_in_salon_tz = today_date_time_in_salon_tz.date()

        three_days_ahead_in_salon_tz = today_date_in_salon_tz + timedelta(days=3)
        two_days_ago_in_salon_tz = today_date_in_salon_tz - timedelta(days=7)

        break_or_off = BreakTimeAndOffDays.objects.filter(
            break_date__range=(two_days_ago_in_salon_tz, three_days_ahead_in_salon_tz),
            staff=request.user.staffprofile,)

        serializer = BarberBreakTimeAndOffDaySerializer(break_or_off, many=True)

        res = break_time_and_offDays_data_with_timezone(data=serializer.data)

        return Response(res, status=status.HTTP_200_OK)


class BarberBreakTimeAndOffDayStatusesAPIView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        statuses = [
            {
                "value": choice.value,
                "label": choice.label,
            }
            for choice in BreakTimeAndOffDays.BlockStatus
        ]


        return Response(statuses, status=HTTP_200_OK)

