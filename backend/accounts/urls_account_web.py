

from django.urls import path

from backend.accounts.views import Barbers_Web_View

urlpatterns = [

    path("barbers/", Barbers_Web_View.as_view(), name="all-barbers"),
    path("barbers/<int:pk>/", Barbers_Web_View.as_view(), name="single-barber"),

    # path(
    #     "barbers/me/",
    #     MyBarberAccountView.as_view(),
    #     name="my-barber-account",
    # ),


]