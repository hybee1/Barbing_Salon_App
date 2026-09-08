
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class SessionBoundTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Refresh serializer that prevents refresh-token rotation from
    extending the user's original authenticated session indefinitely.

    The refresh token must contain an absolute `session_exp` timestamp.
    """

    def validate(self, attrs):
        # Validate/decode the submitted refresh token first.
        refresh = self.token_class(attrs["refresh"])

        session_exp = refresh.get("session_exp")

        if session_exp is None:
            raise serializers.ValidationError(
                "Invalid refresh token."
            )

        try:
            session_exp = int(session_exp)
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                "Invalid refresh token."
            )

        # Enforce the original absolute session deadline.
        now = int(timezone.localtime().timestamp())

        if now >= session_exp:
            raise serializers.ValidationError(
                "Session expired. Please log in again."
            )

        # Let SimpleJWT perform its normal refresh/rotation/blacklisting.
        data = super().validate(attrs)

        # ROTATE_REFRESH_TOKENS=True causes SimpleJWT to return
        # a newly-created refresh token.
        #
        # That new token gets a new normal `exp`, but it must retain
        # the ORIGINAL absolute session deadline.
        new_refresh_token = data.get("refresh")

        if new_refresh_token:
            new_refresh = self.token_class(new_refresh_token)
            new_refresh["session_exp"] = session_exp
            data["refresh"] = str(new_refresh)

        return data
