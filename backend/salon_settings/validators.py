
import pycountry

from django.core.exceptions import ValidationError


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


