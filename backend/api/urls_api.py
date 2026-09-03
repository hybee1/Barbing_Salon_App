
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView

from backend.accounts.views import  CookieTokenRefreshView
from backend.dashboard_auth_and_page.views_dashboard_auth_api import (
                    staff_dashboard_login_api, logout_api)



urlpatterns = [

    # STAFF URLS
    path('staffs/', include('backend.accounts.urls_account_dashboard')),

    # BOOKINGS URLS
    path('bookings/', include('backend.bookings.urls_bookings_dashboard')),

    # BREAK-PERIOD URLS
    path('break-periods/', include('backend.breakperiods.urls_break_periods_dashboard')),

    # SERVICES, HAIRSTYLE AND COLORS URLS
    path('services/', include('backend.services.urls_services_dashboard')),
    path('hairstyles/', include('backend.services.urls_hairstyles_dashboard')),
    path('colors/', include('backend.services.urls_colors_dashboard')),

    # CORE SALON SETTINGS
    path('settings/', include('backend.salon_settings.urls_api')),

    # INVENTORY
    path('inventory/', include('backend.inventory.urls_inventory_dashboard')),

    # REPORTS
    path('reports/', include('backend.reports.urls_reports_dashboard')),

    # DASHBOARD URLS
    path('dashboard/', include('backend.dashboard_stats.urls')),

    # STAFF LOGIN API ENDPOINT
    path("staff/login/", staff_dashboard_login_api, name="staff_dashboard_login"),
    path("staff/logout/", logout_api, name="logout"),

    # AUTH API ENDPOINT
    path("auth/staff-login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),


]