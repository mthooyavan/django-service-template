from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler


class NotAuthorizedError(APIException):
    """Request failed due to unauthorized access"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Not authorized"
    default_code = "not_authorized"


def exception_handler(exc, context):

    # if Django raises a validation error, let's say in .save method, it won't be handled by DRF
    # and end up raising a 500 Internal Error; So here we are converting Django's Validation errors into DRF's
    # validation errors
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            exc = DRFValidationError(detail=exc.message_dict)
        elif hasattr(exc, 'message'):
            exc = DRFValidationError(detail=exc.message)
        elif hasattr(exc, 'messages'):
            exc = DRFValidationError(detail=exc.messages)

    return drf_exception_handler(exc, context)
