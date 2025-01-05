import time

from django.core.cache import cache
from django.http import HttpResponseForbidden

from apps.user.models import BlockedIp


class RateLimitMiddleware:
    """
    10 soniya ichida 5 tadan ko'p so'rov yuborgan IP-manzillarni bloklaydi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = request.META.get("REMOTE_ADDR")
        if not BlockedIp.objects.filter(ip=client_ip).exists():
            current_time = time.time()

            # IP uchun keshni tekshirish yoki yangi ro'yxat yaratish
            ip_cache_key = f"rate_limit_{client_ip}"
            request_times = cache.get(ip_cache_key, [])

            # Eski so'rovlarni tozalash
            request_times = [t for t in request_times if current_time - t < 2]

            # Yangi so'rov vaqtini qo'shish
            request_times.append(current_time)
            cache.set(ip_cache_key, request_times, timeout=2)

            # Limitni tekshirish
            if len(request_times) > 5:
                BlockedIp.objects.create(ip=client_ip)
                return HttpResponseForbidden(
                    "Siz juda ko'p so'rov yubordingiz va siz bloklandingiz. Iltimos, ismoilov000d@gmail.com murojaat qiling."
                )

            # So'rovni davom ettirish
            return self.get_response(request)

        # Agar IP bloklangan bo'lsa
        return HttpResponseForbidden("Siz bloklangansiz!")
