import sys
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    JWT_COOKIE_SECURE=(bool, True),
    JWT_COOKIE_SAMESITE=(str, "Lax"),
    JWT_COOKIE_DOMAIN=(str, ""),
    JWT_ACCESS_LIFETIME_MIN=(int, 15),
    JWT_REFRESH_LIFETIME_DAYS=(int, 7),
)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
# nuxt (ssr) всегда ходит на backend по внутреннему docker-хосту "backend:8000" —
# этот хост должен быть разрешен независимо от того, что задано в DJANGO_ALLOWED_HOSTS
if "backend" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("backend")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "accounts",
    "core",
    "catalog",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

# Боевая база всегда собирается из отдельных POSTGRES_*
# DATABASE_URL — только для тестов (sqlite), задается явно и никогда не участвует в проде.
# pytest-django читает эту настройку раньше, чем успевает отработать 
# conftest.py (os.environ.setdefault там же), поэтому под pytest подставляем
# sqlite и без переменной окружения.
_default_database_url = "sqlite:///test.db" if "pytest" in sys.modules else ""
_database_url = env("DATABASE_URL", default=_default_database_url)
if _database_url:
    DATABASES = {"default": environ.Env.db_url_config(_database_url)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB", default="app"),
            "USER": env("POSTGRES_USER", default="app"),
            "PASSWORD": env("POSTGRES_PASSWORD", default="app"),
            "HOST": env("POSTGRES_HOST", default="postgres"),
            "PORT": env("POSTGRES_PORT", default="5432"),
        }
    }

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 4,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env("JWT_ACCESS_LIFETIME_MIN")),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env("JWT_REFRESH_LIFETIME_DAYS")),
}

# Настройки cookie, которые используют accounts.views и accounts.authentication
JWT_ACCESS_COOKIE = "access"
JWT_REFRESH_COOKIE = "refresh"
JWT_COOKIE_SECURE = env("JWT_COOKIE_SECURE")
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", default="Lax")
JWT_COOKIE_DOMAIN = env("JWT_COOKIE_DOMAIN") or None

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# nginx терминирует TLS и проксирует по http, сам django видит обычный
# http-запрос, поэтому схему берем из заголовка, который nginx проставляет
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# в проде (DEBUG=0) отдаем эти cookie только по https; в деве (DEBUG=1) —
# по http, иначе браузер их просто отбросит
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = env("DJANGO_STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))
MEDIA_URL = "/media/"
MEDIA_ROOT = env("DJANGO_MEDIA_ROOT", default=str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
