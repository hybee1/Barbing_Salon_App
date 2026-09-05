
import logging
import time

logger = logging.getLogger("security")


class RequestSecurityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()

        response = self.get_response(request)

        duration = time.monotonic() - start

        ip = request.META.get("REMOTE_ADDR", "unknown")

        user_id = getattr(
            getattr(request, "user", None),
            "pk",
            None,
        )

        logger.info(
            "request method=%s path=%s status=%s "
            "ip=%s user_id=%s duration=%.3fs",
            request.method,
            request.path,
            response.status_code,
            ip,
            user_id,
            duration,
        )

        return response