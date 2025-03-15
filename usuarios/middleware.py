# middleware.py
from django.utils import timezone

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Actualizar last_seen solo cada 30 segundos para optimizar
            if not request.user.last_seen or (timezone.now() - request.user.last_seen).seconds > 30:
                request.user.last_seen = timezone.now()
                request.user.save(update_fields=['last_seen'])
        
        return response