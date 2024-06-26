"""
Django settings for backend_service project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

import environ
from corsheaders.defaults import default_headers

from backend_service.logging import SensitiveDataFilter
from utils import enums

# django-environ is a package that allows you to utilize 12factor inspired environment variables
# in your settings, securely store configuration variables and switch configurations easily.
# More about django-environ here: https://django-environ.readthedocs.io/en/latest/
ENV = environ.Env()

# Load all the environment variables
environ.Env.read_env()


def env_get(key, default=None):
    """
    Get the environment variable corresponding to the key, if not found, return the default value

    Args:
        key (str): The key of the environment variable
        default (str): The default value to return if the environment variable is not found

    Returns:
        str: The value of the environment variable corresponding to the key, if not found, return the default value
    """
    return os.environ.get(key, default)


# Get the environment setting (development, staging, production, etc.)
ENVIRONMENT = ENV.str("ENVIRONMENT", default="development")
# Use different color codes for different environments (just for visual differentiation)

ENVIRONMENT_COLOR = "#808080"
if ENVIRONMENT == "production":
    ENVIRONMENT_COLOR = "#FF0000"
elif ENVIRONMENT == "staging":
    ENVIRONMENT_COLOR = "#F4C430"

# BASE_DIR is a constant in Django that gets the root directory of the project
# Here it's one level up the directory where settings.py resides
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Debug mode: development environment by default, can be changed by setting DEBUG environment variable
DEBUG = ENV.bool("DEBUG", default=True)

# Booleans indicating if it's a production or staging environment
IS_PROD = ENV.bool("IS_PRODUCTION", default=ENVIRONMENT == "production")
IS_STAGING = ENV.bool("IS_STAGING", default=ENVIRONMENT == "staging")

PERFORMANCE_ANALYSIS = DEBUG and not IS_PROD

# Related URLs
FRONTEND_APP_DOMAINS = ENV.list(
    "FRONTEND_APP_DOMAINS",
    default=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
)
ADMIN_ENDPOINT = ENV.str("ADMIN_ENDPOINT", default="management/portal/")

# A list of strings representing the host/domain names that this Django site can serve.
ALLOWED_HOSTS = ENV.list("ALLOWED_HOSTS", default=["localhost"])
if FRONTEND_APP_DOMAINS:
    ALLOWED_DOMAINS = [
        domain.replace("http://", "").replace("https://", "")
        for domain in FRONTEND_APP_DOMAINS
    ]
    ALLOWED_HOSTS.extend(ALLOWED_DOMAINS)

# IP addresses that are considered 'safe' and can be trusted.
# It's used by IPAddressAuthentication class which is used for IP address based authentication.
WHITELISTED_IP_ADDRESSES = ENV.list("WHITELISTED_IP_ADDRESSES", default=[])
WHITELISTED_CIDR = ENV.list("WHITELISTED_CIDR", default=[])

# If True, the SecurityMiddleware redirects all non-HTTPS requests to HTTPS
# (except for those URLs matching a regular expression listed in SECURE_REDIRECT_EXEMPT).
SECURE_SSL_REDIRECT = ENV.bool("SECURE_SSL_REDIRECT", default=IS_PROD or IS_STAGING)

# SESSION_COOKIE_SECURE is a setting that determines whether to use a secure cookie for the session cookie.
# If set to True, the cookie will be marked as "secure", which means it will only be sent over HTTPS connections.
# It's recommended to set this to True in production to ensure the confidentiality of session data.
SESSION_COOKIE_SECURE = ENV.bool("SESSION_COOKIE_SECURE", default=True)

# CSRF_COOKIE_SECURE is a setting that determines whether to use a secure cookie for the CSRF protection cookie.
# If set to True, the cookie will be marked as "secure", which means it will only be sent over HTTPS connections.
# It's recommended to set this to True in production to prevent CSRF attacks in cases where the attacker might
# be able to intercept HTTP traffic.
CSRF_COOKIE_SECURE = ENV.bool("CSRF_COOKIE_SECURE", default=True)

# CSRF (Cross Site Request Forgery) Trusted Origins settings to prevent CSRF attacks
CSRF_TRUSTED_ORIGINS = ENV.list(
    "CSRF_TRUSTED_ORIGINS",
    default=(
        FRONTEND_APP_DOMAINS
        + [
            "http://localhost:8080",
            "http://localhost:8081",
            "http://localhost:8082",
        ]
    ),
)
# CORS (Cross-Origin Resource Sharing) settings to any requests from a different origin or not
CORS_ALLOW_ALL_ORIGINS = ENV.bool(
    "CORS_ALLOW_ALL_ORIGINS",
    default=not (IS_PROD or IS_STAGING),
)
# If CORS_ALLOW_ALL_ORIGINS is False, then CORS_ALLOWED_ORIGINS should be set to a list of origins that are allowed
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = ENV.list(
        "CORS_ALLOWED_ORIGINS",
        default=(
            FRONTEND_APP_DOMAINS
            + [
                "http://localhost:8080",
                "http://localhost:8081",
                "http://localhost:8082",
            ]
        ),
    )
# CORS_ALLOW_HEADERS is a list of HTTP headers that are allowed in a preflight request.
CORS_ALLOW_HEADERS = list(default_headers) + ENV.list(
    "CORS_ALLOW_HEADERS",
    default=[
        "x-api-key",
    ],
)

# Append backslash to the end of the URL
APPEND_SLASH = True

# SECRET_KEY is a secret unique key for your particular Django installation.
# This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
# This key needs to be shared with any other microservices if they need to verify the signature of
# the JWT token generated by this service.
SECRET_KEY = ENV.str(
    "SECRET_KEY",
    default="lS_gKajWA13liuGKQz7Yd8P-fiqu_U379xsK3VVAD0PgblinxjpNIElQMt4hIB52OtW0xHybPzMLrUf9sK3KqQ",
)

# This section configures Redis URL and settings for Celery.
# Celery is a Distributed Task Queue, which can be used to offload long-running tasks and schedule tasks.
REDIS_URL = ENV.str("REDIS_URL", default=None)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
# Timeout for message visibility in the queue (helps to deal with crashed workers)
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}  # 1 hour
CELERY_IMPORTS = ("communications.tasks",)  # Where your tasks are located
# Worker will acknowledge the task after it has been executed
CELERY_TASKS_ACK_LATE = ENV.bool("CELERY_TASKS_ACK_LATE", default=False)

# PostgreSQL Database configurations
POSTGRES_USER = ENV.str("POSTGRES_USER", default="dev")
POSTGRES_PASSWORD = ENV.str("POSTGRES_PASSWORD", default="dev")
POSTGRES_DB = ENV.str("POSTGRES_DB", default="dashboard_dev")
POSTGRES_PORT = ENV.int("POSTGRES_PORT", default=5432)
PRIMARY_POSTGRES_HOST = ENV.str("PRIMARY_POSTGRES_HOST", default="localhost")
SECONDARY_POSTGRES_HOST = ENV.str("SECONDARY_POSTGRES_HOST", default=None)

# AWS Configuration
AWS_ACCESS_KEY = ENV("AWS_ACCESS_KEY", default=None)
AWS_SECRET_KEY = ENV("AWS_SECRET_KEY", default=None)
AWS_REGION = ENV("AWS_REGION", default="ap-south-1")
AWS_BUCKET_REGION = ENV("AWS_BUCKET_REGION", default="ap-south-1")
AWS_BUCKET = ENV("AWS_BUCKET", default="s2c-platform-staging")
AWS_BUCKET_PUBLIC = f"{AWS_BUCKET}-public"

# Email
EMAIL_FROM = ENV.str("EMAIL_FROM", default="no-reply@example.com")

AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = AWS_SECRET_KEY
AWS_SES_REGION_NAME = ENV("AWS_SES_REGION_NAME", default=AWS_REGION)

# Application definition
REST_FRAMEWORK_APPS = [
    "rest_framework",  # Django REST Framework
    "rest_framework.authtoken",  # Django REST Framework Token Authentication
    "rest_framework_simplejwt.token_blacklist",  # Django REST Framework Simple JWT Token Blacklist
]

THIRD_PARTY_APPS = [
    "corsheaders",  # CORS Headers
    "drf_yasg",  # Swagger
    "phonenumber_field",  # Phone Number Field
    "django_extensions",  # Django Extensions
]

PROJECT_APPS = [
    "communications",  # Communications
    "engineering",  # Engineering
]

INSTALLED_APPS = (
    [
        "backend_service.admin.AdminConfig",  # Admin Config (Custom Admin)
        "django.contrib.auth",  # Django Authentication
        "django.contrib.contenttypes",  # Django Content Types
        "django.contrib.sessions",  # Django Sessions
        "django.contrib.messages",  # Django Messages
        "django.contrib.staticfiles",  # Django Static Files
    ]
    + REST_FRAMEWORK_APPS
    + THIRD_PARTY_APPS
    + PROJECT_APPS
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS Middleware
    "django.middleware.security.SecurityMiddleware",  # Django Security Middleware
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Whitenoise Middleware
    "django.contrib.sessions.middleware.SessionMiddleware",  # Django Session Middleware
    "django.middleware.locale.LocaleMiddleware",  # Django Locale Middleware
    "django.middleware.common.CommonMiddleware",  # Django Common Middleware
    "django.middleware.csrf.CsrfViewMiddleware",  # Django CSRF Middleware
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Django Authentication Middleware
    "django.contrib.messages.middleware.MessageMiddleware",  # Django Messages Middleware
    "backend_service.middleware.LoggingMiddleware",  # Logging Middleware
]

# HEALTH CHECKS
# ------------------------------------------------------------------------------
# Kubernetes Health Checks in Django
# https://www.ianlewis.org/en/kubernetes-health-checks-django
# Add this to the beginning of your MIDDLEWARE_CLASSES to add health checks to your app.
# Putting it at the beginning of MIDDLEWARE_CLASSES ensures it gets run before
# other Middleware classes that might access the database.
MIDDLEWARE.insert(0, "backend_service.middleware.HealthCheckMiddleware")  # noqa F405

ROOT_URLCONF = "backend_service.urls"

DISK_USAGE_MAX = ENV.int("DISK_USAGE_MAX", default=80)
MEMORY_MIN = ENV.int("MEMORY_MIN", default=30)
HEALTH_CHECK = {
    "DISK_USAGE_MAX": DISK_USAGE_MAX,  # percent
    "MEMORY_MIN": MEMORY_MIN,  # in MB
}

DJANGO_LOG_LEVEL = ENV("DJANGO_LOG_LEVEL", default="DEBUG")
APP_LOG_LEVEL = ENV("APP_LOG_LEVEL", default="DEBUG")
LOG_PATH = ENV("LOG_PATH", default="/code/logs")

LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": (
                    "[{asctime}] [{module}] [{process:d}] [{thread:d}] [{org_id}] "
                    "[{user_id}] [{correlation_id}] [{levelname}] {message}"
                ),
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            },
            "simple": {
                "format": "[{asctime}] [{process:d}] [{org_id}] [{user_id}] [{correlation_id}] [{levelname}] {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            },
        },
        "filters": {
            "mask_sensitive_data": {
                "()": SensitiveDataFilter,
            },
        },
        "handlers": {
            "console": {
                "level": APP_LOG_LEVEL,
                "filters": ["mask_sensitive_data"],
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": DJANGO_LOG_LEVEL,
                "propagate": True,
            },
            "default": {
                "handlers": ["console"],
                "level": APP_LOG_LEVEL,
                "propagate": False,
            },
        },
    }
try:
    os.makedirs(LOG_PATH, exist_ok=True)
except PermissionError:
    pass
else:
    # If the directory was created successfully, add the file handler
    LOGGING["handlers"]["file"] = {
        "level": APP_LOG_LEVEL,
        "filters": ["mask_sensitive_data"],
        "class": "logging.FileHandler",
        "filename": f"{LOG_PATH}/debug.log",
        "formatter": "verbose",
    }
    LOGGING["loggers"]["django"]["handlers"].append("file")
    LOGGING["loggers"]["default"]["handlers"].append("file")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "backend_service.context_processors.environment_variables",
            ],
        },
    },
]

# Enabling WSGI by default, comment out and uncomment ASGI_APPLICATION to use ASGI
WSGI_APPLICATION = "backend_service.wsgi.application"
# ASGI_APPLICATION = "backend_service.asgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": PRIMARY_POSTGRES_HOST,
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "PORT": POSTGRES_PORT,
    }
}

if SECONDARY_POSTGRES_HOST:
    DATABASES["slave"] = {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": SECONDARY_POSTGRES_HOST,
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "PORT": POSTGRES_PORT,
    }
    DATABASE_ROUTERS = ["backend_service.routers.database.MasterSlaveRouter"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "backend_service.validators.PasswordCombinationValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

AUTHENTICATION_BACKENDS = [
    # Django ModelBackend is the default authentication backend.
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "backend_service.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("backend_service.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "backend_service.pagination.PageNumberPagination",
    "PAGE_SIZE": ENV.int("DEFAULT_PAGE_SIZE", default=20),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "standard": ENV.str("STANDARD_THROTTLE_RATE", default="500/minute"),
        "auth": ENV.str("AUTH_THROTTLE_RATE", default="5/minute"),
    },
    "EXCEPTION_HANDLER": "backend_service.exceptions.exception_handler",
}

SIMPLE_JWT = {
    "ALGORITHM": "HS512",
    "USER_ID_FIELD": "uuid",
    "AUTH_TOKEN_CLASSES": ("backend_service.authentication.AccessToken",),
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

LANGUAGES = enums.LANGUAGES


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STORAGES = {
    "default": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Swagger Settings

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "VALIDATOR_CLASS": None,
}

REDOC_SETTINGS = {"LAZY_RENDERING": True}

# Create a superuser account on application start-up
# ------------------------------------------------------------------------------
SUPERUSER_EMAIL = ENV("SUPERUSER_EMAIL", default="mail@thooyavan.me")
SUPERUSER_PASSWORD = ENV("SUPERUSER_PASSWORD", default="Nasike@123")
SUPERUSER_FULL_NAME = ENV("SUPERUSER_FULL_NAME", default="Thooyavan Manivaasakar")

# Create a test user account on application start-up
# ------------------------------------------------------------------------------
TEST_USER_UUID = ENV("TEST_USER_UUID", default="7382a34d-5d40-409d-9027-60cd9567c88d")
TEST_USER_EMAIL = ENV("TEST_USER_EMAIL", default="test@thooyavan.me")
TEST_USER_PASSWORD = ENV("TEST_USER_PASSWORD", default="Nasike@123")
TEST_USER_FULL_NAME = ENV("TEST_USER_FULL_NAME", default="Test User")
