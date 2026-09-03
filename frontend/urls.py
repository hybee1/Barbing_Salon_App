
from django.urls import path
from frontend import views

urlpatterns = [

    path("", views.homePage),

    path("bookings/", views.bookingPage),

    path("gallery/hairstyles/", views.hairstyleGallery),


]