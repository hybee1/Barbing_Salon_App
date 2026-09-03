
from rest_framework import serializers
from backend.accounts.serializers import StaffProfileSerializer
from backend.breakperiods.models import BreakTimeAndOffDays


class BreakTimeAndOffDaysSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer()

    # staff = serializers.PrimaryKeyRelatedField(
    #     queryset=StaffProfile.objects.all()
    # )

    class Meta:
        model = BreakTimeAndOffDays
        fields = "__all__"


class ActiveBreakTimeSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.username", read_only=True)

    class Meta:
        model = BreakTimeAndOffDays
        fields = ["staff_username", "start_time", "end_time"]


class BarberBreakTimeAndOffDaySerializer(serializers.ModelSerializer):
    # staff = StaffProfileSerializer(read_only=True)

    # staff = serializers.PrimaryKeyRelatedField(
    #     queryset=StaffProfile.objects.all(), read_only=True
    # )

    class Meta:
        model = BreakTimeAndOffDays
        fields = ["date", "start_time", "end_time", "reason", "status"]



