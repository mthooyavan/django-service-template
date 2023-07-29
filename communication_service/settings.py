"""
Django settings for communication_service project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

import environ
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# django-environ is being used to enable environment variable parsing/casting
ENV = environ.Env()
# Load all the environment variables
environ.Env.read_env()


def env_get(key, default=None):
    return os.environ.get(key, default)


ENVIRONMENT = ENV.str('ENVIRONMENT', default='development')
ENVIRONMENT_COLOR = '#FF0000' if ENVIRONMENT == 'production' else '#F4C430' if ENVIRONMENT == 'staging' else '#808080'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = ENV.bool('DEBUG', default=True)

IS_PROD = ENV.bool('IS_PRODUCTION', default=(ENVIRONMENT == 'production'))
IS_STAGING = ENV.bool('IS_STAGING', default=(ENVIRONMENT == 'staging'))

ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS', default=['localhost'])

WHITELISTED_IP_ADDRESSES = ENV.list('WHITELISTED_IP_ADDRESSES', default=[])
WHITELISTED_CIDR = ENV.list('WHITELISTED_CIDR', default=[])

SECURE_SSL_REDIRECT = ENV('SECURE_SSL_REDIRECT', default=IS_PROD or IS_STAGING, cast=bool)

if IS_PROD or IS_STAGING:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    sentry_sdk.init(
        dsn=ENV('SENTRY_DSN', default=None),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration()
        ],
        server_name=ENV('SERVER_NAME', default=ENV('SERVER_NAME', default='server-not-set')),
        release=ENV('SOURCE_VERSION', default=ENV('RELEASE_VERSION', default='default-release')),
        environment=ENVIRONMENT)

SECRET_KEY = ENV('SECRET_KEY', default='^3!@kpi9pfi&lqmsh_7f_@(f*z#r!&35q836^uha3wa!$e!g@y')

# SQL Database
DATABASE_USER = ENV('DATABASE_USER', default='dev')
DATABASE_PASSWORD = ENV('DATABASE_PASSWORD', default='dev')
DATABASE_HOST = ENV('DATABASE_HOST', default='127.0.0.1')
DATABASE_NAME = ENV('DATABASE_NAME', default='dev')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-Party Apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'phonenumber_field',

    'django_extensions',

    # Health Check
    'health_check',                             # required
    'health_check.db',                          # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.celery',              # requires celery
    'health_check.contrib.celery_ping',         # requires celery
    'health_check.contrib.psutil',              # disk and memory utilization; requires psutil
    'health_check.contrib.redis',               # requires Redis broker
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'communication_service.urls'

DISK_USAGE_MAX = ENV.int('DISK_USAGE_MAX', default=80)
MEMORY_MIN = ENV.int('MEMORY_MIN', default=30)
HEALTH_CHECK = {
    'DISK_USAGE_MAX': DISK_USAGE_MAX,  # percent
    'MEMORY_MIN': MEMORY_MIN,    # in MB
}

if ENV.bool('FILE_LOGGING', default=False):
    LOG_PATH = ENV('LOG_PATH', default='/code/logs')
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            "debug_file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": f"{LOG_PATH}/debug.log",
            },
            "info_file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": f"{LOG_PATH}/info.log",
            },
            "warning_file": {
                "level": "WARNING",
                "class": "logging.FileHandler",
                "filename": f"{LOG_PATH}/warning.log",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "filename": f"{LOG_PATH}/error.log",
            },
            "critical_file": {
                "level": "CRITICAL",
                "class": "logging.FileHandler",
                "filename": f"{LOG_PATH}/critical.log",
            },
        },
        "loggers": {
            "default": {
                "handlers": [
                    "console",
                    "debug_file",
                    "info_file",
                    "warning_file",
                    "error_file",
                    "critical_file"
                ],
                "level": ENV("DJANGO_LOG_LEVEL", default="INFO"),
                "propagate": True,
            },
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": ENV.bool('DISABLE_EXISTING_LOGGERS', default=False),
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "default": {
                "handlers": ["console", ],
                "level": ENV("DJANGO_LOG_LEVEL", default="DEBUG"),
                "propagate": True,
            },
        },
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'communication_service.context_processors.environment_variables',
            ],
        },
    },
]

WSGI_APPLICATION = 'communication_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core_central_service.validators.PasswordCombinationValidator',
    }
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'communication_service.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'communication_service.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'standard': '500/minute',
        'auth': '5/minute',
    },

    'EXCEPTION_HANDLER': 'communication_service.exceptions.exception_handler'

}

if ENVIRONMENT == 'production':
    # This disables the 'browsable' api that can cause various production issues
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'UPDATE_LAST_LOGIN': True,
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STORAGES = {
    "default": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'