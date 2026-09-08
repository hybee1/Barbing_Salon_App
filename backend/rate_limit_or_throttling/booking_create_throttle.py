from rest_framework.throttling import AnonRateThrottle


class BookingCreateThrottle(AnonRateThrottle):
    scope = "booking_create"
