

from django.urls import path
from backend.bookings.views import (CreateBookingView, BarberBookingAvailabilityApiView)


urlpatterns = [

    path("create/", CreateBookingView.as_view(), name="create_booking"),

    path("barber/availability/", BarberBookingAvailabilityApiView.as_view(), name="available-barbers")


]