from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.accounts.models import User, StaffProfile
from backend.bookings.booking_services import create_booking, update_booking
from backend.bookings.models import Booking
from backend.services.models import Service, Hairstyle, Color
from backend.utils.services import BarberScheduler


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
        read_only_fields = [ "booking_reference", "status",  ]

    def validate_customer_name(self, value):
        value = " ".join(value.split())

        if len(value) < 3:
            raise serializers.ValidationError(
                "customer name is too short."
            )

        return value

    def validate_barber(self, value):

        if value.user.role != User.Role.STAFF:
            raise serializers.ValidationError("Selected user is not a staff member.")

        if not value.user.is_active:
            raise serializers.ValidationError("Selected barber/stylist is inactive.")

        if value.status != StaffProfile.StaffStatus.ACTIVE:
            raise serializers.ValidationError("Selected barber/stylist is not currently active.")

        if not BarberScheduler().can_receive_bookings(value):
            raise serializers.ValidationError(
                "Selected staff member cannot receive bookings."
            )

        return value

    def validate(self, attrs):
        if ( attrs.get("status") == Booking.STATUS.CANCELLED and not attrs.get("reason_for_cancellation")  ):
            raise serializers.ValidationError(
                { "reason_for_cancellation": "A cancellation reason is required." }
            )

        return attrs


class CreateBookingSerializer(serializers.ModelSerializer):

    barber = serializers.PrimaryKeyRelatedField(
        queryset=StaffProfile.objects.filter(
            user__is_active=True,
            status=StaffProfile.StaffStatus.ACTIVE, )
    )

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
    )

    hairstyle = serializers.PrimaryKeyRelatedField(
        queryset=Hairstyle.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    color = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Booking
        fields = [
                    "booking_reference", "barber", "service", "hairstyle", "color",
                    "price", "customer_name", "phone_number", "booking_date",
                    "start_time", "booking_source", "booked_by",
        ]

    def validate_customer_name(self, value):
        value = " ".join(value.split())

        if len(value) < 3:
            raise serializers.ValidationError(
                "customer name is too short."
            )

        return value


    def validate_barber(self, value):

        if value.user.role != User.Role.STAFF:
            raise serializers.ValidationError("Selected user is not a staff member.")

        if not value.user.is_active:
            raise serializers.ValidationError("Selected barber/stylist is inactive.")

        if value.status != StaffProfile.StaffStatus.ACTIVE:
            raise serializers.ValidationError("Selected barber/stylist is not currently active.")

        if not BarberScheduler().can_receive_bookings(value):
            raise serializers.ValidationError(
                "Selected staff member cannot receive bookings."
            )

        return value

    def validate(self, attrs):

        salon_config, _ = BarberScheduler().get_salon_config()
        open_time = salon_config["open_time"]
        close_time = salon_config["close_time"]
        booking_date = attrs.get("booking_date")
        start_time = attrs.get("start_time")

        barber= attrs.get("barber")
        service = attrs.get("service")
        hairstyle = attrs.get("hairstyle")
        color = attrs.get("color")

        service_price = service.price
        service_duration_minutes = service.duration_minutes

        #  validate if barber can receive bookings
        if not BarberScheduler().can_receive_bookings(barber):
            raise serializers.ValidationError({
                "details": "selected staff member can not receive bookings."
            })

        #  validate if hairstyle belongs to that service
        if hairstyle and hairstyle.service_id != service.id:
            raise serializers.ValidationError({
                "hairstyle": "Hairstyle does not belong to the selected service."
            })

        hairstyle_price = hairstyle.price if hairstyle else 0
        hairstyle_duration_minutes = ( hairstyle.duration_minutes if hairstyle else 0 )

        #  validate if color belongs to that service
        if color and color.service_id != service.id:
            raise serializers.ValidationError({
                "color": "Color does not belong to the selected service."
            })

        color_price = color.price if color else 0
        color_duration_minutes = ( color.duration_minutes if color else 0 )

        if booking_date < timezone.localdate():
            raise serializers.ValidationError({ "booking_date": "Booking date cannot be in the past."})

        total_duration = timedelta(
            minutes=service_duration_minutes + hairstyle_duration_minutes + color_duration_minutes
        )

        if total_duration > timedelta(hours=3):
            raise serializers.ValidationError({"time": "Invalid session duration, Invalid session duration"
                                                       " is unexpectedly longer than 3 hours."})

        # validate start_time is not less than salon open time
        if start_time < open_time:
            raise serializers.ValidationError({"time": "Invalid time, selected time is before salon open time."})

        end_time = start_time + total_duration

        # validate end_time greater than salon close time
        if end_time > close_time:
            raise serializers.ValidationError({"time": "Invalid duration time, session duration is "
                                                       "beyond salon close time."})
        # manually attach price
        attrs["price"] = service_price + hairstyle_price + color_price


        return attrs

    def create(self, validated_data):

        return create_booking( barber_id=validated_data["barber"].pk,
                               service_id=validated_data["service"].pk,
                               hairstyle_id=(
                                                validated_data["hairstyle"].pk
                                                if validated_data.get("hairstyle")
                                                else None
                                            ),
                               color_id=(
                                            validated_data["color"].pk
                                            if validated_data.get("color")
                                            else None
                                        ),
                               total_price=validated_data["price"],
                               booking_date=validated_data["booking_date"],
                               start_time=validated_data["start_time"],
                               end_time=validated_data["end_time"],
                               customer_name=validated_data["customer_name"],
                               phone_number=validated_data["phone_number"],
                               booking_source=validated_data["booking_source"],
                               booked_by=validated_data["booked_by"] )


class UpdateBookingSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField( choices=Booking.STATUS.choices, required=True, )

    reason_for_cancellation = serializers.CharField( required=False, allow_blank=True, allow_null=True, )

    class Meta:
        model = Booking
        fields = [ "status", "reason_for_cancellation", ]

    def validate(self, attrs):

        status = attrs.get("status")
        reason = attrs.get("reason_for_cancellation")

        # Cancellation requires a reason
        if status == Booking.STATUS.CANCELLED and not reason:
            raise serializers.ValidationError({
                "reason_for_cancellation":
                    "A cancellation reason is required when cancelling a booking."
            })

        # Reason only makes sense for cancelled bookings
        if status != Booking.STATUS.CANCELLED and reason:
            raise serializers.ValidationError({
                "reason_for_cancellation":
                    "A cancellation reason can only be provided "
                    "when cancelling a booking."
            })

        return attrs

    def update(self, instance, validated_data):

        return update_booking(
            booking_reference=instance.booking_reference,
            status=validated_data["status"],
            reason_for_cancellation=validated_data.get(
                "reason_for_cancellation"
            ),
        )



class BookingSuccessFullyCreatedReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [ "booking_reference", "price", "status", "booking_source", "booked_by", ]


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

    def validate_total_service_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError( "Duration must be greater than zero." )

        if value > 24 * 60:
            raise serializers.ValidationError( "Duration is too large." )

        return value


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






