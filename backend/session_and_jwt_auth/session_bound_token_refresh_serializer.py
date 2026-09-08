from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class SessionBoundTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Prevents refresh-token rotation from extending the
    original authenticated session indefinitely.
    """

    def validate(self, attrs):
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

        now = int(timezone.localtime().timestamp())

        if now >= session_exp:
            raise serializers.ValidationError(
                "Session expired. Please log in again."
            )

        # Let SimpleJWT perform its normal refresh,
        # rotation and blacklisting.
        data = super().validate(attrs)

        # Preserve the ORIGINAL absolute session deadline
        # on the rotated refresh token.
        new_refresh_token = data.get("refresh")

        if new_refresh_token:
            new_refresh = self.token_class(new_refresh_token)

            new_refresh["session_exp"] = session_exp

            data["refresh"] = str(new_refresh)

        # Make the original deadline available to the view
        # so it can calculate cookie max_age.
        data["session_exp"] = session_exp

        return data
