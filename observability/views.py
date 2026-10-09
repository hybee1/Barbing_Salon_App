
from django.db import connection
from django.http import JsonResponse


def live(request):
    """
    Liveness check.

    If Django can execute this view, the process is alive.
    """
    return JsonResponse( { "status": "ok",  } )


def ready(request):
    """
    Readiness check.

    Checks whether the application can communicate
    with its database.
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            { "status": "ok", "database": "ok", }
        )

    except Exception:
        return JsonResponse(
            { "status": "error", "database": "unavailable", },
            status=503,
        )

