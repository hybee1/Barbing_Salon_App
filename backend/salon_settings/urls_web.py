

from django.urls import path

from backend.salon_settings.views import SalonInfoWebView

urlpatterns = [

    path( "salon-info-web/",  SalonInfoWebView.as_view(), name="salon-info-web", ),

]