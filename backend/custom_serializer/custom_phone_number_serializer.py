
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumbers import NumberParseException
import phonenumbers
from rest_framework import serializers

from backend.utils.services import BarberScheduler


class SalonPhoneNumberFieldCustomSerializer(PhoneNumberField):

    def to_internal_value(self, data):
        salon_config, _ = BarberScheduler().get_salon_config()
        country = salon_config["country"]
        print("1")
        try:
            phone = phonenumbers.parse(str(data), country)
            print("1a")
        except NumberParseException:
            print("1b")
            raise serializers.ValidationError( "The phone number entered is not valid." )
        print("2")
        if not phonenumbers.is_valid_number(phone):
            print("2a")
            raise serializers.ValidationError( "The phone number entered is not valid." )
        print("3")
        if phonenumbers.region_code_for_number(phone) != country:
            print("3a")
            raise serializers.ValidationError( "Phone number must match the salon's country." )

        print("from phone_number serializer, phone = ", phone)

        return phone