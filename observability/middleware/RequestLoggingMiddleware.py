import logging
import time
import uuid

logger = logging.getLogger(__name__)


# class RequestLoggingMiddleware:
# new RequestIDMiddleware

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
RESPONSE_REQUEST_ID_HEADER = "X-Request-ID"


class RequestLoggingMiddleware:
    """
    Gives every HTTP request a request ID.

    If the client/proxy already supplied X-Request-ID,
    reuse it. Otherwise generate one.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(
            REQUEST_ID_HEADER
        ) or str(uuid.uuid4())

        request.request_id = request_id

        start_time = time.monotonic()

        response = None

        try:
            response = self.get_response(request)
            return response

        finally:
            duration_ms = round(
                (time.monotonic() - start_time) * 1000,
                2,
            )

            status_code = (
                response.status_code
                if response is not None
                else 500
            )

            logger.info(
                "http_request",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )

            if response is not None:
                response[RESPONSE_REQUEST_ID_HEADER] = request_id