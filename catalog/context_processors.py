from django.conf import settings


def store(request):
    return {
        "store_name": settings.STORE_NAME,
        "store_email": settings.STORE_EMAIL,
        "store_phone": settings.STORE_PHONE,
        "store_address": settings.STORE_ADDRESS,
    }
