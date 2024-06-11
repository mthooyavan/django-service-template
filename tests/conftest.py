"""
Testing configuration.

Source: https://bit.ly/2OudJ0R

Note: this may be redundant with pytest.ini.
"""
import os

import django
from django.conf import settings

# We manually designate which settings we will be using in an environment variable
# This is similar to what occurs in the `manage.py`
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_service.settings.test")


def pytest_configure():
    settings.DEBUG = False
    settings.WHITELISTED_IP_ADDRESSES = ["*"]
    settings.task_always_eager = True
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}
    django.setup()
