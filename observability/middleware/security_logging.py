
import logging


logger = logging.getLogger("security")


class SecurityLoggingMiddleware:
    """
    Logs security-relevant request context such as
    client IP and authenticated user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = None

        try:
            response = self.get_response(request)
            return response

        finally:
            user = getattr(request, "user", None)

            user_id = getattr(user, "pk", None)

            logger.info(
                "security_request",
                extra={
                    "request_id": getattr(
                        request,
                        "request_id",
                        None,
                    ),
                    "method": request.method,
                    "path": request.path,
                    "status_code": (
                        response.status_code
                        if response is not None
                        else 500
                    ),
                    "ip": request.META.get(
                        "REMOTE_ADDR",
                        "unknown",
                    ),
                    "user_id": user_id,
                },
            )

'''            
Now your security logs can look like:

security_request
request_id=abc123
method=POST
path=/api/login
status_code=401
ip=192.168.1.20
user_id=None
That is much more useful when investigating suspicious activity.
'''