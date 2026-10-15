
from django.urls import path
from backend.services.views import ServicesView, ServiceWithItHairstylesAndColorsApiView

urlpatterns = [

    path("", ServicesView.as_view(), name="all-services-web"),

    path("<int:pk>/hairstylesandcolors/", ServiceWithItHairstylesAndColorsApiView.as_view(),
         name="service-hairstyles-colors"),

]