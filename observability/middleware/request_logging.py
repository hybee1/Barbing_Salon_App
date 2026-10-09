
import logging
import time


logger = logging.getLogger("observability")

#  This handles general HTTP observability.
class RequestLoggingMiddleware:
    """
    Logs basic information about every HTTP request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = None

        try:
            response = self.get_response(request)
            return response

        finally:
            duration_ms = round(
                (time.monotonic() - start) * 1000,
                2,
            )

            logger.info(
                "http_request",
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
                    "duration_ms": duration_ms,
                },
            )
'''           
    This gives you logs such as:
    
    http_request
    request_id=abc123
    method=GET
    path=/api/orders
    status_code=200
    duration_ms=42.31
    Notice that it uses the request ID middleware but doesn't create the ID itself.
'''