
from django.urls import path
from backend.bookings.views import (BookingForLast7Days_Api_View, TodayBooking_Api_View,
                                    BarberUpcomingBookingsToday, ManageBooking_Api_View,
                                    OneBarberBookingForLast7Days_Api_View, OneBarberBookingsToday)


urlpatterns = [

    path("", ManageBooking_Api_View.as_view(), name="manage-booking"),

    path( "<str:booking_reference>/", ManageBooking_Api_View.as_view(), name="update-booking", ),

    # ONLY THOSE WHO CAN RECEIVE BOOKING CAN VIEW THIS ENDPOINT
    path("barber/last7days/", OneBarberBookingForLast7Days_Api_View.as_view(), name="one-barber-bookings-last-7-days"),

    # ONLY SALON MANAGER AND RECEPTIONIST
    path("last7days/", BookingForLast7Days_Api_View.as_view(), name="admin-view-bookings-last-7-days"),

    path("admin/today/", TodayBooking_Api_View.as_view(), name="today_bookings"),

    # ONLY THOSE WHO CAN RECEIVE BOOKING CAN VIEW THIS ENDPOINT
    path("barber/today/", OneBarberBookingsToday.as_view(), name="barber-booking-today"),

    # ONLY THOSE WHO CAN RECEIVE BOOKING CAN VIEW THIS ENDPOINT
    path("barber/upcoming/today/", BarberUpcomingBookingsToday.as_view(),
                        name="one-barber-upcoming-booking-today"),

    # ONLY SALON MANAGER AND RECEPTIONIST
    path("upcoming/today/", BarberUpcomingBookingsToday.as_view(),
                        name="admin-view-barber-upcoming-booking-today"),

]