from rest_framework import serializers

from backend.accounts.models import User, StaffProfile
from backend.bookings.models import Booking
from backend.services.models import Service, Hairstyle, Color


class BookingSerializer(serializers.ModelSerializer):

    barber = serializers.PrimaryKeyRelatedField(
        queryset=StaffProfile.objects.all()
    )

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )

    hairstyle = serializers.PrimaryKeyRelatedField(
        queryset=Hairstyle.objects.all(),
        required=False,
        allow_null=True,
    )

    color = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Booking
        fields = [
                    "id", "booking_reference", "barber", "service", "hairstyle", "color",
                    "price", "customer_name", "email", "phone_number", "booking_date",
                    "arrival_time", "start_time", "end_time", "status",
                    "reason_for_cancellation",
                    "booking_source", "booked_by",
        ]
        read_only_fields = ["booking_reference"]

    def validate_customer_name(self, value):
        value = " ".join(value.split())

        if len(value) < 3:
            raise serializers.ValidationError(
                "customer name is too short."
            )

        return value

    def validate_barber(self, value):
        if value.user.role != User.Role.STAFF:
            raise serializers.ValidationError(
                "Selected user is not a staff member."
            )

        return value

    def validate(self, attrs):
        if (
            attrs.get("status") == Booking.STATUS.CANCELLED
            and not attrs.get("reason_for_cancellation")
        ):
            raise serializers.ValidationError(
                {
                    "reason_for_cancellation":
                        "A cancellation reason is required."
                }
            )

        return attrs


class BookingReadSerializer(serializers.ModelSerializer):

    staff_name = serializers.CharField(source="barber.user.username", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    hairstyle_name = serializers.CharField(source="hairstyle.name", read_only=True)
    color_name = serializers.CharField(source="color.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
                    "id", "booking_reference", "price", "customer_name", "email",
                    "phone_number", "booking_date", "arrival_time",
                    "start_time", "end_time", "status", "reason_for_cancellation",
                    "booking_source", "booked_by",

                    "staff_name", "service_name", "hairstyle_name", "color_name"]


# class BarberAvailableTimeQuerySerializer(serializers.Serializer):
class BarberAvailableTimeQuerySerializer(serializers.Serializer):

    barber_id = serializers.IntegerField()
    date = serializers.DateField()
    total_service_duration = serializers.IntegerField()


class BarberBookingStatsSerializer(serializers.Serializer):
    today_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    upcoming_count = serializers.IntegerField()
    break_status = serializers.CharField()

class BarberBookingsTodaySerializer(serializers.ModelSerializer):

    service = serializers.CharField(source="service.name", read_only=True)
    hairstyle = serializers.CharField(source="hairstyle.name", read_only=True)

    class Meta:
        model = Booking
        fields = ["start_time", "customer_name", "service", "hairstyle", "status",]






