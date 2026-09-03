#
# from django.urls import path
# from rest_framework_simplejwt.views import TokenObtainPairView
#
# from api.accounts.views import CookieTokenRefreshView
#
#
# urlpatterns = [
#     path("auth/staff-login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
#     # path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
#
#     # path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
#
#     path("auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
#
#
# ]