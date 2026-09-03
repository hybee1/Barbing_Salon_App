from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.breakperiods.serializers import (BarberBreakTimeAndOffDaySerializer,
                                              BreakTimeAndOffDaysSerializer,
                                                ActiveBreakTimeSerializer)
from backend.custom_permissions.permissions import Is_Authenticated_Staff_User


class CreateBarberBreakTimeAndOffDayAPIView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated

    def post(self, request):
        print("CreateBarberBreakTimeAndOffDayAPIView POST 1")
        data = request.data
        print("CreateBarberBreakTimeAndOffDayAPIView POST 2")
        data['staff'] = request.user.staffprofile.pk
        print("data = ", data)
        print("CreateBarberBreakTimeAndOffDayAPIView POST 3")

        serializer = BreakTimeAndOffDaysSerializer(data=data)
        print("CreateBarberBreakTimeAndOffDayAPIView POST 4")

        serializer.is_valid(raise_exception=True)
        print("CreateBarberBreakTimeAndOffDayAPIView POST 5")

        serializer.save()
        print("CreateBarberBreakTimeAndOffDayAPIView POST 6")

        return Response("successful", status=status.HTTP_200_OK)


class Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView(APIView):
    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated

    def get(self, request):
        print("Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView GET 1")
        today = timezone.localdate()
        three_days_ahead = today + timedelta(days=3)
        seven_days_ago = today - timedelta(days=7)
        print("Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView GET 2")

        break_or_off = BreakTimeAndOffDays.objects.filter(
            date__range=(seven_days_ago, three_days_ahead))

        print("Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView GET 3")

        serializer = BreakTimeAndOffDaysSerializer(break_or_off, many=True)

        print("Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView GET 4")
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActiveBreakTimeAndOffDayAPIView(APIView):
    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated

    def get(self, request):
        print("ActiveBreakTimeAndOffDayAPIView GET 1")
        today = timezone.localtime()
        today_date = today.date()
        current_time = today.time()
        print("ActiveBreakTimeAndOffDayAPIView GET 2")

        active_break = BreakTimeAndOffDays.objects.filter( date=today_date,
                               start_time__lte=current_time, end_time__gte=current_time )

        print("ActiveBreakTimeAndOffDayAPIView GET 3")

        serializer = ActiveBreakTimeSerializer(active_break, many=True)

        print("ActiveBreakTimeAndOffDayAPIView GET 4")
        print("serializer for active break = ", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OneBarberBreakTimeAndOffDayAPIView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated

    #  this return between seven days ago and three days ahead for that barber
    def get(self, request):
        today = timezone.localdate()
        three_days_ahead = today + timedelta(days=3)
        two_days_ago = today - timedelta(days=7)

        break_or_off = BreakTimeAndOffDays.objects.filter(
            date__range=(two_days_ago, three_days_ahead),
            staff=request.user.staffprofile,)

        serializer = BarberBreakTimeAndOffDaySerializer(break_or_off, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberBreakTimeAndOffDayStatusesAPIView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        print("BarberBreakTimeAndOffDayStatusesAPIView 1")

        statuses = [
            {
                "value": choice.value,
                "label": choice.label,
            }
            for choice in BreakTimeAndOffDays.BlockStatus
        ]

        print("statuses = ", statuses)

        print("BarberBreakTimeAndOffDayStatusesAPIView 2")

        return Response(statuses, status=HTTP_200_OK)

