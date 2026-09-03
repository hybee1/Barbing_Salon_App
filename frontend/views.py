
from django.shortcuts import render


def homePage(request):
    return render(request, "index.html")

def bookingPage(request):
    return render(request, "booking.html")

def hairstyleGallery(request):
    return render(request, "gallery.html")

