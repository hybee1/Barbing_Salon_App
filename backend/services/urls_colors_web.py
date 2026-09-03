
from django.urls import path
from api.services.views import ColorsView


# urlpatterns = [
#     path("", ColorsView.as_view(), name="all-colors"),
#     path("<int:pk>/", ColorsView.as_view(), name="single-color"),
#     path("add/", ColorsView.as_view(), name="add-color"),
#     path("delete/", ColorsView.as_view(), name="delete-one-or-more-colors"),
# ]