

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

        # Present when ROTATE_REFRESH_TOKENS=True.
        new_refresh_token = serializer.validated_data.get("refresh")

        response = Response(
            {"detail": "Token refreshed."},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="accessToken",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        if new_refresh_token:
            response.set_cookie(
                key="refreshToken",
                value=new_refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

        return response
