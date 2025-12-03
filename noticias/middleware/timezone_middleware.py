from django.utils import timezone
from ..utils import get_client_ip, get_user_timezone

class AutoTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        user_tz = get_user_timezone(ip)
        timezone.activate(user_tz)

        response = self.get_response(request)
        return response
