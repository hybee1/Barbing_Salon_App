from babel.numbers import get_currency_symbol
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    CURRENCY_LOCALES = {
        "NGN": "en_NG",
        "USD": "en_US",
        "GBP": "en_GB",
        "EUR": "en_IE",
        "CAD": "en_CA",
        "CHF": "en_CH",
        "AUD": "en_AU",
    }

    def get_paginated_response(self, data, currency=None):
        response = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }

        if currency:
            locale = self.CURRENCY_LOCALES.get(currency, "en_US")
            response["currency"] = get_currency_symbol( currency, locale=locale, )

        return Response(response)
