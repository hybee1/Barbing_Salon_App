import phonenumbers
import pycountry
from django.core.cache import cache
from phonenumbers import NumberParseException

from backend.salon_settings.models import SalonBookingSetting, SalonInfo
from backend.salon_settings.serializers import SalonBookingSettingSerializer, SalonInfoReadSerializer


def normalize_country(value):
    from backend.exceptions.exceptions import InvalidCountryError
    if not value:
        raise InvalidCountryError(value)

    value = str(value).strip()

    try:
        country = pycountry.countries.lookup(value)
    except LookupError:
        raise InvalidCountryError(value)

    return country.alpha_2


def normalize_phone_number(value, country):
    #  the value is the phone number
    from backend.exceptions.exceptions import (InvalidCountryError, InvalidPhoneNumberError)
    if not value:
        raise InvalidPhoneNumberError(value)

    if not country:
        raise InvalidCountryError(country)

    country_code = normalize_country(country)

    value = str(value).strip()

    try:
        phone = phonenumbers.parse(
            value,
            country_code,
        )
    except NumberParseException:
        raise InvalidPhoneNumberError(value)

    if not phonenumbers.is_valid_number(phone):
        raise InvalidPhoneNumberError(value)

    phone_country = phonenumbers.region_code_for_number(phone)

    if phone_country != country_code:
        raise InvalidPhoneNumberError(value)

    return phonenumbers.format_number(
        phone,
        phonenumbers.PhoneNumberFormat.E164,
    )


def normalize_currency(value):
    from backend.exceptions.exceptions import InvalidCurrencyError
    if not value:
        raise InvalidCurrencyError(value)

    value = str(value).strip().upper()

    currency = pycountry.currencies.get(alpha_3=value)

    if not currency:
        raise InvalidCurrencyError(value)

    return currency.alpha_3


@staticmethod
def get_salon_info_config():
    key = "salon_info_data"
    config = cache.get(key)

    if config is not None:
        return config

    salon_info = SalonInfo.objects.first()

    if not salon_info:
        raise Exception("Salon info settings not found")

    config = SalonInfoReadSerializer(salon_info).data
    cache.set(key, config, timeout=None)

    return config


@staticmethod
def get_salon_booking_config():
    key = "salon_booking_config"
    config = cache.get(key)

    if config is not None:
        return config

    salon_booking = SalonBookingSetting.objects.first()

    if not salon_booking:
        raise Exception("Salon booking settings not found")


    config = SalonBookingSettingSerializer(salon_booking).data
    cache.set(key, config, timeout=None)

    return config

