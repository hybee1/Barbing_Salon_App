import os

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from backend.accounts.models import User
from backend.rate_limit_or_throttling.login_rate_throttle import LoginRateThrottle


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_api(request):

    refresh = request.COOKIES.get("refreshToken")

    if refresh:
        try:

            RefreshToken(refresh).blacklist()

        except Exception:

            pass

    # IMPORTANT: destroy Django's session too
    logout(request)

    response = Response( status=status.HTTP_204_NO_CONTENT )

    response.delete_cookie(
        "accessToken",
        path="/",
        samesite="Lax",
    )

    response.delete_cookie(
        "refreshToken",
        path="/",
        samesite="Lax",
    )


    return response
    # return Response( status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def staff_dashboard_login_api(request):

    username_or_phone = request.data.get("username")
    password = request.data.get("password")

    if not username_or_phone or not password:
        return Response(
            {"message": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(
        Q(username=username_or_phone) |
        Q(phone_number=username_or_phone)
    ).first()

    if user is None:
        return Response(
            {"message": "Invalid login credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = authenticate(
        username=user.username,
        password=password
    )

    if user is None:
        return Response(
            {"message": "Invalid login credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # ---------------------------------------------------------
    # 1. Create Django session
    # ---------------------------------------------------------

    login(request, user)

    # Absolute session lifetime: 2 hours
    # SESSION_LIFETIME = 60 * 60 * 2
    SESSION_LIFETIME = os.getenv("SESSION_LIFETIME")

    request.session.set_expiry(SESSION_LIFETIME)
    request.session.save()

    # Get the ACTUAL session expiry timestamp
    session_expiry = request.session.get_expiry_date()

    session_exp_timestamp = int( session_expiry.timestamp() )

    # ---------------------------------------------------------
    # 2. Create JWT
    # ---------------------------------------------------------

    refresh = RefreshToken.for_user(user)

    # Store the absolute Django-session expiry
    # inside the refresh token.
    refresh["session_exp"] = session_exp_timestamp

    # Access token must never live beyond the session.
    access_token = refresh.access_token

    # now_timestamp = int( datetime.now(timezone.utc).timestamp() )
    now_timestamp = int(timezone.localtime().timestamp())

    remaining_seconds = max( 0, session_exp_timestamp - now_timestamp )

    # Normal access token lifetime is 15 minutes,
    # but it must not exceed the session lifetime.
    # access_lifetime = min( 60 * 15, remaining_seconds )
    access_lifetime = min(60 * int(os.getenv("ACCESS_TOKEN_LIFETIME")), remaining_seconds)

    # Override the access token expiry
    access_token["exp"] = now_timestamp + access_lifetime

    # ---------------------------------------------------------
    # 3. Response
    # ---------------------------------------------------------

    response = JsonResponse({ "redirect_url": user_based_dashboard(user) })

    secure = not settings.DEBUG

    # Access token cookie
    response.set_cookie(
        "accessToken",
        str(access_token),
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=access_lifetime,
    )

    # Refresh token cookie
    response.set_cookie(
        "refreshToken",
        str(refresh),
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=remaining_seconds,
    )

    return response


def user_based_dashboard(user):

    '''
    # the reason for this method is, for you to access the staff/salon manager 
    # dashboard, you must have been authenticated, and the dashboard to show depends 
    # on the authenticated user's permissions, that is why you were first directed to 
    # this path "/staff/staff-dashboard/" with method signature "def user_based_dashboard(user):"
    # given that you have been authenticated then 
    # that path/method directs you to "staff/staff-dashboard/" with method signature
    # "def permission_based_staff_dashboard_page(request):" which internally determine which 
    # dashboard to show to you.
    #  
    # 
    # notice the leading slash
    # the view for which is below will return the right template based on permission
    '''
    return (f"/web/staff/staff-dashboard/")





