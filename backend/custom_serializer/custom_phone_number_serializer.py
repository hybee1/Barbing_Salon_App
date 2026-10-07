
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumbers import NumberParseException
import phonenumbers
from rest_framework import serializers

from backend.utils.services import BarberScheduler


class SalonPhoneNumberFieldCustomSerializer(PhoneNumberField):

    def to_internal_value(self, data):
        salon_config, _ = BarberScheduler().get_salon_config()
        country = salon_config["country"]

        try:
            phone = phonenumbers.parse(str(data), country)

        except NumberParseException:

            raise serializers.ValidationError( "The phone number entered is not valid." )

        if not phonenumbers.is_valid_number(phone):

            raise serializers.ValidationError( "The phone number entered is not valid." )

        if phonenumbers.region_code_for_number(phone) != country:

            raise serializers.ValidationError( "Phone number must match the salon's country." )

        return phone