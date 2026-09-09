
import pycountry
import pytz

from django.core.exceptions import ValidationError
from backend.exceptions.exceptions import InvalidCountryError, InvalidTimezoneError
from backend.salon_settings.services_salon_config import normalize_country


def validate_country_code(value):
    if not value:
        raise ValidationError("Country is required.")

    value = str(value).strip().upper()

    country = pycountry.countries.get(alpha_2=value)

    if country is None:
        raise ValidationError(
            f"Invalid ISO country code: {value}."
        )


def validate_currency_code(value):
    if not value:
        raise ValidationError("Currency is required.")

    value = str(value).strip().upper()

    currency = pycountry.currencies.get(alpha_3=value)

    if currency is None:
        raise ValidationError(
            f"Invalid ISO currency code: {value}."
        )


def validate_timezone_for_country(*, timezone: str,country: str,v) -> str:

    country = normalize_country(country)

    country_code = country.alpha_2

    valid_timezones = pytz.country_timezones.get(country_code)

    if not valid_timezones:
        raise InvalidCountryError(
            f"No timezone information found for country "
            f"{country_code}."
        )

    if timezone not in valid_timezones:
        raise InvalidTimezoneError(
            f"'{timezone}' is not a valid timezone for "
            f"{country}."
        )

    return timezone

