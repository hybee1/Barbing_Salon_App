

from django.urls import path

from backend.salon_settings.views import (SalonBookingSettingView, SalonConfig_And_Info_View,
                                          SalonInfoModifyView)

urlpatterns = [

    path( "salon-config-info/", SalonConfig_And_Info_View.as_view(), name="salon-config-info", ),

    path( "salon-info/",  SalonInfoModifyView.as_view(), name="salon-info", ),

    path(  "salon-booking-buffer/", SalonBookingSettingView.as_view(),
        name="salon-booking-buffer",
    ),


]