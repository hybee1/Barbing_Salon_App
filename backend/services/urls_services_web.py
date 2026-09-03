
from django.urls import path
from backend.services.views import ServicesView, Service_With_It_Hairstyles_And_Colors_Api_View

urlpatterns = [

    path("", ServicesView.as_view(), name="all-services-web"),

    path("<int:pk>/hairstylesandcolors/", Service_With_It_Hairstyles_And_Colors_Api_View.as_view(),
         name="service-hairstyles-colors"),

]