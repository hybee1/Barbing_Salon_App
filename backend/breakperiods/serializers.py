from datetime import timedelta, datetime, date, timezone as dt_timezone
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.accounts.models import StaffProfile
from backend.accounts.serializers import StaffProfileSerializer
from backend.breakperiods.break_periods_services import create_break_period
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.utils.services import BarberScheduler


class BreakTimeAndOffDaysSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)

    # staff = serializers.PrimaryKeyRelatedField(
    #     queryset=StaffProfile.objects.all(),
    # )

    class Meta:
        model = BreakTimeAndOffDays
        fields = "__all__"
        read_only_fields = ( "staff", "break_date", )

    def validate(self, attrs):
        # the two immediate lines below are expected to be in utc as commented in the model
        break_start_date_time_utc: datetime = attrs.get("break_start_date_time")
        break_end_date_time_utc: datetime = attrs.get("break_end_date_time")

        break_status = attrs.get("status")

        salon_config, _ = BarberScheduler().get_salon_config()
        salon_tz = ZoneInfo(salon_config["time_zone"])
        salon_open_time = salon_config["open_time"]
        salon_close_time = salon_config["close_time"]

        break_start_date_time_in_salon_tz = break_start_date_time_utc.astimezone(salon_tz)
        break_end_date_time_in_salon_tz = break_end_date_time_utc.astimezone(salon_tz)

        break_date_in_salon_tz: date = break_start_date_time_in_salon_tz.date()

        salon_today_date_time_in_salon_tz = timezone.now().astimezone(salon_tz)
        salon_today_date_in_salon_tz = salon_today_date_time_in_salon_tz.date()

        salon_open_time_in_salon_tz = datetime.combine(break_start_date_time_in_salon_tz.date(),
                                                       salon_open_time, tzinfo=salon_tz)
        salon_close_time_in_salon_tz = datetime.combine(break_start_date_time_in_salon_tz.date(),
                                                        salon_close_time, tzinfo=salon_tz)

        if break_start_date_time_in_salon_tz > break_end_date_time_in_salon_tz:
            raise serializers.ValidationError({"details": "Break end time must be after start time."})

        try:
            break_status_enum = BreakTimeAndOffDays.BlockStatus(break_status)

        except ValueError:
            raise serializers.ValidationError({ "details": "Invalid break status." })

        if break_status_enum == BreakTimeAndOffDays.BlockStatus.BREAK:

            three_days_ahead = salon_today_date_in_salon_tz + timedelta(days=3)

            if break_date_in_salon_tz > three_days_ahead:
                raise ValidationError({"date": "Date cannot be more than three days ahead."})

            if ((break_start_date_time_in_salon_tz < salon_open_time_in_salon_tz) or
                    (break_start_date_time_in_salon_tz > salon_close_time_in_salon_tz)):

                raise serializers.ValidationError({"details": "Break start time must be with "
                                                              "salon working hours."})

            if (break_end_date_time_in_salon_tz - break_start_date_time_in_salon_tz > timedelta(hours=1)):
                raise serializers.ValidationError({"details": "Break duration can not be more than one hour."})

        # OFF_DAY is complete off from work for the entire day
        if break_status_enum == BreakTimeAndOffDays.BlockStatus.OFF_DAY:
            three_days_ahead = salon_today_date_in_salon_tz + timedelta(days=3)

            if break_date_in_salon_tz > three_days_ahead:
                raise ValidationError({"date": "Date cannot be more than three days ahead."})

            if ((break_start_date_time_in_salon_tz < salon_open_time_in_salon_tz) or
                    (break_start_date_time_in_salon_tz > salon_close_time_in_salon_tz)):
                raise serializers.ValidationError({"details": "Break start time must be with "
                                                              "salon working hours."})
            # we needed to add the two immediate below lines to attrs because in the next method
            # it expects the two newly added two line in attrs that is why they were added.
            # IMPORTANTLY WE NOTICE THE VALUES WE ADDED.
            # not e we did not add the utc versions of the tow fields as they are already present in attrs
            attrs["break_start_date_time_in_salon_tz"] = salon_open_time_in_salon_tz
            attrs["break_end_date_time_in_salon_tz"] = salon_close_time_in_salon_tz

            return attrs

        if break_status_enum in {BreakTimeAndOffDays.BlockStatus.ON_LEAVE,
                                 BreakTimeAndOffDays.BlockStatus.SICK_LEAVE,
                                 BreakTimeAndOffDays.BlockStatus.PERSONAL,
                                 BreakTimeAndOffDays.BlockStatus.OTHER }:

            if (break_end_date_time_in_salon_tz - break_start_date_time_in_salon_tz < timedelta(hours=6)):
                raise serializers.ValidationError({"details": "duration can not be less than six hours."})

        # we needed to add the two immediate below lines to attrs because in the next method
        # it expects the two newly added two line in attrs that is why they were added.
        # not e we did not add the utc versions of the tow fields as they are already present in attrs
        attrs["break_start_date_time_in_salon_tz"] = break_start_date_time_in_salon_tz
        attrs["break_end_date_time_in_salon_tz"] = break_end_date_time_in_salon_tz

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        return create_break_period(staff_id=request.user.staffprofile.pk,
                                   break_start_date_time_in_salon_tz=validated_data["break_start_date_time_in_salon_tz"],
                                   break_end_date_time_in_salon_tz=validated_data["break_end_date_time_in_salon_tz"],
                                   status=validated_data["status"],
                                   reason=validated_data["reason"])


class ActiveBreakTimeSerializer(serializers.ModelSerializer):
    staff_username = serializers.CharField(source="staff.user.username", read_only=True)

    class Meta:
        model = BreakTimeAndOffDays
        fields = ["staff_username", "break_start_date_time", "break_end_date_time"]


class BarberBreakTimeAndOffDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = BreakTimeAndOffDays
        fields = ["break_date", "break_start_date_time", "break_end_date_time", "reason", "status"]



