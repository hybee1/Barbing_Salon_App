
from django.urls import path
from backend.bookings.views import (BookingForLast7Days_Api_View, TodayBooking_Api_View,
                                    BarberBookingsToday,
                                    BarberUpcomingBookingsToday, BookingView)

urlpatterns = [

    path("", BookingView.as_view(), name="bookings"),

    path("last7days/", BookingForLast7Days_Api_View.as_view(), name="bookings_last_7_days"),

    path("admin/today/", TodayBooking_Api_View.as_view(), name="today_bookings"),

    path("barber/today/", BarberBookingsToday.as_view(), name="barber-booking-stats"),

    path("barber/upcoming/today/", BarberUpcomingBookingsToday.as_view(),
         name="barber-upcoming-booking-today"),

]