
from django.urls import path
from backend.services.views import (ServicesView, ServiceAndItsHairstylesView,
                                    ServiceAndItsColorsView, ServicesWithColorsButOnlyServiceView,
                                    ServicesWithHairstylesButOnlyServiceView)

urlpatterns = [

    path("", ServicesView.as_view(), name="all-services-web"),

    path("<int:pk>/", ServicesView.as_view(), name="single-service"),

    path("<int:pk>/hairstyles/", ServiceAndItsHairstylesView.as_view(), name="service-hairstyles"),
    path("<int:pk>/colors/", ServiceAndItsColorsView.as_view(), name="service-colors"),

    path("add/", ServicesView.as_view(), name="add-service"),
    path("delete/", ServicesView.as_view(), name="delete-one-or-more-services"),

    path("colors/only-service/", ServicesWithColorsButOnlyServiceView.as_view(),
                                                        name="services-colors-only-service"),

    path("hairstyles/only-service/", ServicesWithHairstylesButOnlyServiceView.as_view(),
                                name="services-hairstyles-only-service"),

]