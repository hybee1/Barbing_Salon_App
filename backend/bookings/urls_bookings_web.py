

from django.urls import path
from backend.bookings.views import ( CreateBookingView, BarberBookingAvailability_Api_View )


urlpatterns = [

    path("create/", CreateBookingView.as_view(), name="create_booking"),

    path("barber/availability/", BarberBookingAvailability_Api_View.as_view(),
         name="available-barbers")


]