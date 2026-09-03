
from django.urls import path, include

from backend.dashboard_auth_and_page.views_dashboard_auth_api import user_based_dashboard
from backend.dashboard_auth_and_page.views_dashboard_web_page import (staff_dashboard_login_page,
    permission_based_staff_dashboard_page)

urlpatterns = [


    path('staffs/', include('backend.accounts.urls_account_web')),

    path('bookings/', include('backend.bookings.urls_bookings_web')),

    path('services/', include('backend.services.urls_services_web')),

    path('hairstyles/', include('backend.services.urls_hairstyles_web')),
    # path('colors/', include('api.services.urls_colors_web')),

    # CORE SALON SETTINGS
    path('settings/', include('backend.salon_settings.urls_web')),


    # STAFF LOGIN PAGE
    path("staff/login/", staff_dashboard_login_page, name="staff_dashboard_login"),

    path("staff/dashboard/", user_based_dashboard, name="user-dashboard"),

    path("staff/staff-dashboard/", permission_based_staff_dashboard_page,
         name="permission_based_staff_dashboard"),



]