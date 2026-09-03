
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import SalonInfo, SalonBookingSetting




class SalonInfoReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='salon_name', read_only=True)

    address = serializers.CharField(source='salon_address', read_only=True)
    email = serializers.EmailField(source='salon_email', read_only=True)

    country = serializers.CharField(source='salon_country', read_only=True)

    time_zone = TimeZoneSerializerField(source='salon_time_zone',  read_only=True)

    phone_number = serializers.CharField(source='salon_phone_number', read_only=True)
    currency = serializers.CharField(source='salon_currency', read_only=True)

    open_time = serializers.TimeField(source='salon_open_time', read_only=True)

    close_time = serializers.TimeField(source='salon_close_time', read_only=True)

    class Meta:
        model = SalonInfo
        fields = [
                    "id", "name", "address", "email", "country", "phone_number",
                     "currency", "country", "open_time", "close_time", "time_zone",
                 ]


class SalonInfoWriteSerializer(serializers.ModelSerializer):

    country = serializers.CharField( source="salon_country"  )

    phone_number = serializers.CharField( source="salon_phone_number" )

    time_zone = TimeZoneSerializerField( source="salon_time_zone" )

    name = serializers.CharField( source="salon_name" )

    address = serializers.CharField( source="salon_address" )

    email = serializers.EmailField( source="salon_email" )

    currency = serializers.CharField( source="salon_currency"  )

    open_time = serializers.TimeField( source="salon_open_time" )

    close_time = serializers.TimeField( source="salon_close_time" )

    class Meta:
        model = SalonInfo

        fields = [
            "name", "address", "email", "country", "phone_number",
            "currency", "open_time", "close_time", "time_zone",
        ]

    def validate_country(self, value):
        from .services_salon_config import normalize_country, normalize_phone_number, normalize_currency
        return normalize_country(value)

    def validate_currency(self, value):
        from .services_salon_config import normalize_country, normalize_phone_number, normalize_currency
        return normalize_currency(value)

    def validate(self, attrs):
        country = attrs.get("salon_country")

        if country is None and self.instance:
            country = self.instance.salon_country

        phone = attrs.get("salon_phone_number")

        if phone is not None:

            from ..exceptions.exceptions import InvalidPhoneNumberError, InvalidCountryError

            try:
                from .services_salon_config import normalize_country, normalize_phone_number, normalize_currency
                attrs["salon_phone_number"] = normalize_phone_number(
                    value=phone,
                    country=country,
                )
            except ( InvalidCountryError, InvalidPhoneNumberError, ) as exc:
                raise serializers.ValidationError({ "phone_number": str(exc) })

        open_time = attrs.get("salon_open_time")

        if open_time is None and self.instance:
            open_time = self.instance.salon_open_time

        close_time = attrs.get("salon_close_time")

        if close_time is None and self.instance:
            close_time = self.instance.salon_close_time

        if (
                open_time is not None
                and close_time is not None
                and close_time <= open_time
        ):
            raise serializers.ValidationError({
                "close_time": "Close time must be after open time."
            })

        return attrs


class SalonBookingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalonBookingSetting
        fields = "__all__"


