"""
context processors for communication_service
"""
from django.conf import settings


def environment_variables(_):
    """
    Pass the environment name and color into the template context.
    """
    return {
        'ENVIRONMENT_NAME': settings.ENVIRONMENT,
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT_COLOR,
    }
