from .base import *

DEBUG = False

ADMINS = [
    ("Mikhail Kudryashov", "Alteria2004@gmail.com"),
]

ALLOWED_HOSTS = [
    "backend.nuwa.orange-city.ru",
    "nuwa.orange-city.ru",
]

CORS_ALLOWED_ORIGINS = [
    "https://backend.nuwa.orange-city.ru",
    "https://nuwa.orange-city.ru",
]
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_DOMAIN = ".nuwa.orange-city.ru"

