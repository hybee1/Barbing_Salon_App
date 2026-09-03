
from rest_framework.exceptions import APIException
from rest_framework import status




class BookingConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "booking conflict"

    def __init__(self, start_time, end_time):
        detail = (
            f"The selected period {start_time} - {end_time} "
            "conflicts with an existing booking."
        )
        super().__init__(detail)

class BookingDateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "booking date is in the past"

    def __init__(self, date_time):
        detail = (
            f"The selected date {date_time}  "
            "was observed to be in the past."
        )
        super().__init__(detail)


# class BookingTimeException(APIException):
#     BUSINESS_OPEN_TIME, BUSINESS_CLOSE_TIME = SalonBusinessHour.business_hours()
#
#     status_code = status.HTTP_400_BAD_REQUEST
#     default_detail = (f"Sorry our salon working hours is between "
#                     f"{BUSINESS_OPEN_TIME} and {BUSINESS_CLOSE_TIME}")
#
#     def __init__(self):
#
#         detail = (f"Sorry our salon working hours is between "
#                     f"{self.BUSINESS_OPEN_TIME} and {self.BUSINESS_CLOSE_TIME}"
#         )
#         super().__init__(detail)

class InvalidCountryError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid country."

    def __init__(self, country):
        detail = f'"{country}" is not a valid country.'
        super().__init__(detail)

class InvalidCurrencyError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid currency."

    def __init__(self, currency):
        detail = f'"{currency}" is not a valid currency.'
        super().__init__(detail)

class InvalidPhoneNumberError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid phone number."

    def __init__(self, phone_number):
        detail = (f'"{phone_number}" is not a valid phone number or '
                  f'the phone number does not conform with selected country.')
        super().__init__(detail)

class RoleException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid role"

    def __init__(self):
        detail = f"Invalid role for user"
        super().__init__(detail)

class UserNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "user not found"

    def __init__(self):
        detail = f"user not found."
        super().__init__(detail)

class UserException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "user exception"

    def __init__(self, text):
        detail = f" {text}"
        super().__init__(detail)