
from django.urls import path
from backend.breakperiods.views import (BarberBreakTimeAndOffDayStatusesAPIView,
                                        OneBarberBreakTimeAndOffDayAPIView,
                                        CreateBarberBreakTimeAndOffDayAPIView,
                                        Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView,
                                        ActiveBreakTimeAndOffDayAPIView)

urlpatterns = [

    path("", Last7daysAnd3DaysAheadBarberBreakTimeAndOffDayAPIView.as_view(),
                          name="last-7-days-and-3-days-ahead-break-time-and-off-day-api"),

    path("break/statuses/", BarberBreakTimeAndOffDayStatusesAPIView.as_view(),
         name="all-break-statuses"),

    path("break/create/", CreateBarberBreakTimeAndOffDayAPIView.as_view(),
                                            name="create-break-time-and-off-day"),

    path("break/barber/", OneBarberBreakTimeAndOffDayAPIView.as_view(),
                                            name="one-barber-break-time-and-off-day"),

    path("active-breaks/", ActiveBreakTimeAndOffDayAPIView.as_view(),
                                            name="active-breaks"),



]