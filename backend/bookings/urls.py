
from django.urls import path
from .views import available_slots, create_booking, owner_dashboard
from .views import (
    reception_dashboard, check_in, start_service, complete_service, cancel_booking )

urlpatterns = [
    path("slots/", available_slots, name="available-slots"),
    path("create/", create_booking),

    path("reception/", reception_dashboard),

    path("checkin/<int:booking_id>/", check_in),
    path("start/<int:booking_id>/", start_service),
    path("complete/<int:booking_id>/", complete_service),
    path("cancel/<int:booking_id>/", cancel_booking),

    path("reports/", owner_dashboard),
]




