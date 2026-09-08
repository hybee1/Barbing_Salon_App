from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from backend.session_and_jwt_auth.session_bound_token_refresh_serializer import SessionBoundTokenRefreshSerializer



class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = SessionBoundTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refreshToken")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(
            data={"refresh": refresh_token}
        )

        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data["access"]

        # Only present when ROTATE_REFRESH_TOKENS=True
        new_refresh_token = serializer.validated_data.get("refresh")

        # ---------------------------------------------------------
        # Calculate cookie lifetime from the absolute session expiry
        # ---------------------------------------------------------

        session_exp = serializer.validated_data.get("session_exp")

        if session_exp is None:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        now_timestamp = int(timezone.localtime().timestamp())

        remaining_seconds = max(
            0,
            int(session_exp) - now_timestamp,
        )

        # ---------------------------------------------------------
        # Access-token cookie lifetime
        # ---------------------------------------------------------

        access_lifetime = int(
            settings.SIMPLE_JWT[ "ACCESS_TOKEN_LIFETIME" ].total_seconds()
        )


        access_cookie_max_age = min(
            access_lifetime,
            remaining_seconds,
        )

        response = Response(
            {"detail": "Token refreshed."},
            status=status.HTTP_200_OK,
        )

        # ---------------------------------------------------------
        # Access token cookie
        # ---------------------------------------------------------

        response.set_cookie(
            key="accessToken",
            value=access_token,
            max_age=access_cookie_max_age,
            httponly=settings.AUTH_COOKIE_HTTPONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        # ---------------------------------------------------------
        # Rotated refresh token cookie
        # ---------------------------------------------------------

        if new_refresh_token:
            response.set_cookie(
                key="refreshToken",
                value=new_refresh_token,
                max_age=remaining_seconds,
                httponly=settings.AUTH_COOKIE_HTTPONLY,
                secure=settings.AUTH_COOKIE_SECURE,
                samesite=settings.AUTH_COOKIE_SAMESITE,
            )

        return response
