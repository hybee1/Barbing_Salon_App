import uuid


REQUEST_ID_HEADER = "X-Request-ID"

#  This should be responsible only for creating/propagating the request ID.
class AddRequestCorrelationIDMiddleware:
    """
    Ensures every request has a correlation/request ID.

    Reuses X-Request-ID when supplied by a trusted upstream.
    Otherwise generates a new UUID.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get(REQUEST_ID_HEADER)

        if not request_id:
            request_id = str(uuid.uuid4())

        request.request_id = request_id

        response = self.get_response(request)

        response[REQUEST_ID_HEADER] = request_id

        return response

    '''
    This gives you:

    request.request_id throughout your application. And the client gets:
    
    X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
    '''