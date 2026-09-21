from datetime import timedelta, datetime, date
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.accounts.serializers import StaffProfileSerializer
from backend.breakperiods.break_periods_services import create_break_period
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.utils.services import BarberScheduler


class BreakTimeAndOffDaysSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer()

    # staff = serializers.PrimaryKeyRelatedField(
    #     queryset=StaffProfile.objects.all()
    # )

    class Meta:
        model = BreakTimeAndOffDays
        fields = "__all__"

    def validate(self, attrs):
        break_start_date_time: datetime = attrs.get("break_start_date_time")
        break_end_date_time: datetime = attrs.get("break_end_date_time")
        break_date: date = attrs.get("break_date")
        break_status = attrs.get("status")

        salon_config, _ = BarberScheduler().get_salon_config()
        salon_tz = ZoneInfo(salon_config["time_zone"])
        salon_open_time = salon_config["open_time"]
        salon_close_time = salon_config["close_time"]

        salon_today_date_time = timezone.now().astimezone(salon_tz)
        salon_today_date = salon_today_date_time.date()
        salon_today_time = salon_today_date_time.time()

        break_start_date_time_salon_time = break_start_date_time.astimezone(salon_tz)
        break_end_date_time_salon_time = break_end_date_time.astimezone(salon_tz)

        if break_date < salon_today_date:
            raise ValidationError( {"date": "Date cannot be in the past."} )


        if break_start_date_time_salon_time > break_end_date_time_salon_time:
            raise serializers.ValidationError({"details": "Break end time must be after start time."})

        try:
            break_status_enum = BreakTimeAndOffDays.BlockStatus(break_status)

        except ValueError:
            raise serializers.ValidationError({ "details": "Invalid break status." })

        if break_status_enum == BreakTimeAndOffDays.BlockStatus.BREAK:

            three_days_ahead = salon_today_date + timedelta(days=3)

            if break_date > three_days_ahead:
                raise ValidationError({"date": "Date cannot be more than three days ahead."})

            if (break_start_date_time < salon_open_time) or (break_start_date_time > salon_close_time):
                raise serializers.ValidationError({"details": "Break start time must be with "
                                                              "salon working hours."})

            if ( (break_end_date_time < salon_open_time) or (break_end_date_time > salon_close_time)):
                raise serializers.ValidationError({"details": "Break end time must be with "
                                                              "salon working hours."})

            if (break_end_date_time - break_start_date_time > timedelta(hours=1)):
                raise serializers.ValidationError({"details": "Break duration can not be more than one hour."})

        if break_status_enum in { BreakTimeAndOffDays.BlockStatus.OFF_DAY, BreakTimeAndOffDays.BlockStatus.ON_LEAVE,
                            BreakTimeAndOffDays.BlockStatus.SICK_LEAVE, BreakTimeAndOffDays.BlockStatus.PERSONAL,
                            BreakTimeAndOffDays.BlockStatus.OTHER,
        }:

            if (break_end_date_time - break_start_date_time < timedelta(hours=6)):
                raise serializers.ValidationError({"details": "duration can not be less than six hours."})

        return attrs

    def create(self, validated_data):

        return create_break_period( staff_id=validated_data["staff"].pk,
                               break_start_date_time=validated_data["break_start_date_time"],
                               break_end_date_time=validated_data["break_end_date_time"],
                               status=validated_data["status"],
                               reason=validated_data["reason"] )


class BreakTimeAndOffDaysSerializer(serializers.ModelSerializer):

    staff_name = serializers.CharField(source="staff.user.username", read_only=True)

    class Meta:
        model = BreakTimeAndOffDays
        fields = [
                    "id", "break_date", "break_start_date_time",
                    "break_end_date_time", "status", "reason",
                 ]


class ActiveBreakTimeSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.username", read_only=True)

    class Meta:
        model = BreakTimeAndOffDays
        fields = ["staff_username", "break_start_date_time", "break_end_date_time"]


class BarberBreakTimeAndOffDaySerializer(serializers.ModelSerializer):
    # staff = StaffProfileSerializer(read_only=True)

    # staff = serializers.PrimaryKeyRelatedField(
    #     queryset=StaffProfile.objects.all(), read_only=True
    # )

    class Meta:
        model = BreakTimeAndOffDays
        fields = ["break_date", "break_start_date_time", "break_end_date_time", "reason", "status"]



