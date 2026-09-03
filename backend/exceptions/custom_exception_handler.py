from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import exception_handler


import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    logger.exception(exc)

    response = exception_handler(exc, context)

    if response is not None:
        return Response(
            {
                "success": False,
                "error": response.data,
            },
            status=response.status_code,
        )

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed,)):
        response.status_code = 401
        response.data = {
            "detail": response.data.get("detail", "Authentication credentials are "
                                                  "invalid or have expired."),
            "code": "authentication_required",
            "logout_required": True,
        }
        return response

    return Response(
        {
            "success": False,
            "error": getattr(exc, "detail", str(exc))
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


