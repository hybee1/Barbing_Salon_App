
from django.urls import path
from backend.salon_services.views import ServicesView, ServiceWithItHairstylesAndColorsApiView

urlpatterns = [

    path("", ServicesView.as_view(), name="all-services-web"),

    path("<int:pk>/hairstylesandcolors/", ServiceWithItHairstylesAndColorsApiView.as_view(),
         name="service-hairstyles-colors"),

]