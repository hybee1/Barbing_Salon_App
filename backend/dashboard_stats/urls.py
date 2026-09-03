

from django.urls import path
from backend.bookings.views import BarberBookingStatsView, BarberBookingsToday
from backend.dashboard_stats.views import SalonManagerDashboardStatsView



urlpatterns = [

    # DASHBOARD ENDPOINT
    path("admin/stats/", SalonManagerDashboardStatsView.as_view(),
                                            name="salon-manager-dashboard-stats"),

    path("barber/stats/", BarberBookingStatsView.as_view(), name="barber-booking-stats"),



    # path("dashboard/breaks/today/", AllBarberBreakTimeAndOffDayAPIView.as_view(),
    #      name="barber-booking-stats"),


]