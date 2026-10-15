

from django.urls import path

from backend.accounts.views import BarbersWebView

urlpatterns = [

    path("barbers/", BarbersWebView.as_view(), name="all-barbers"),
    path("barbers/<int:pk>/", BarbersWebView.as_view(), name="single-barber"),

    # path(
    #     "barbers/me/",
    #     MyBarberAccountView.as_view(),
    #     name="my-barber-account",
    # ),


]