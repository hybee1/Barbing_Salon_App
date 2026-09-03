# ==========================================================
# urls_reports_dashboard.py
# ==========================================================

from django.urls import path

from .views import (
    ManagerReportView,
    ManagerDateRangeReportView,
)


urlpatterns = [

    path(
        "",
        ManagerReportView.as_view(),
        name="manager-report"
    ),

    path(
        "range/",
        ManagerDateRangeReportView.as_view(),
        name="manager-date-range-report"
    ),

]
