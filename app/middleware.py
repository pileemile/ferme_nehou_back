from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return JsonResponse({
                'error': 'Trop de requêtes. Veuillez réessayer dans quelques instants.'
            }, status=429)