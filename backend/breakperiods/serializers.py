from datetime import timedelta
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
        break_start_date_time = attrs.get("break_start_date_time")
        break_end_date_time = attrs.get("break_end_date_time")
        break_date = attrs.get("break_date")
        break_status = attrs.get("status")

        salon_config, _ = BarberScheduler().get_salon_config()
        salon_tz = ZoneInfo(salon_config["time_zone"])
        salon_open_time = salon_config["open_time"]
        salon_close_time = salon_config["close_time"]

        salon_today_date_time = timezone.localtime().astimezone(salon_tz)
        salon_today_date = salon_today_date_time.data()
        salon_today_time = salon_today_date_time.time()

        if break_date < salon_today_date:
            raise ValidationError( {"date": "Date cannot be in the past."} )

        three_days_ahead = salon_today_date_time + timedelta(days=3)

        if break_date > three_days_ahead:
            raise ValidationError( {"date": "Date cannot be more than three days ahead."} )

        if break_start_date_time > break_end_date_time:
            raise serializers.ValidationError({"details": "Break end time must be after start time."})

        if break_status.lower() == BreakTimeAndOffDays.BlockStatus.BREAK:
            if ( (break_start_date_time < salon_open_time) or (break_start_date_time > salon_close_time)):
                raise serializers.ValidationError({"details": "Break start time must be with "
                                                              "salon working hours."})

            if ( (break_end_date_time < salon_open_time) or (break_end_date_time > salon_close_time)):
                raise serializers.ValidationError({"details": "Break end time must be with "
                                                              "salon working hours."})

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



