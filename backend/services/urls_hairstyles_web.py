
from django.urls import path
from backend.services.views import HairstylesView

urlpatterns = [

    path("", HairstylesView.as_view(), name="all-hairstyles"),
    path("<int:pk>/", HairstylesView.as_view(), name="single-hairstyle"),
    path("add/", HairstylesView.as_view(), name="add-hairstyle"),
    path("delete/", HairstylesView.as_view(), name="delete-one-or-more-hairstyles"),

]