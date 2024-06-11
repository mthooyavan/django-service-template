from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import APIException as DefaultAPIException
from rest_framework.exceptions import ValidationError as DRFValidationError


class APIException(DefaultAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _("A server error occurred.")
    default_code = "INTERNAL_SERVER_ERROR"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        super().__init__(detail=detail, code=code)


class AuthenticationFailedAPIException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Incorrect credentials")
    default_code = "AUTH_FAILED"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        super().__init__(detail=detail, code=code)
        self.detail = {"detail": detail}


class InvalidTokenAPIException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Token is invalid or expired")
    default_code = "AUTH_FAILED"


class MethodNotAllowedAPIException(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = _("Method not allowed")
    default_code = "METHOD_NOT_ALLOWED"


class LockOutExceptionAPIException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Account is locked out")
    default_code = "LOCKED_OUT"

    def __init__(self, wait=None, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        super().__init__(detail=detail, code=code)
        self.detail = {"detail": _("Account is locked out for 300 seconds")}


class DisabledAccountAPIException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Account is disabled")
    default_code = "AUTH_FAILED"


class IncompleteAccountAPIException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Account details is incomplete")
    default_code = "AUTH_FAILED"


class NotAuthorizedAPIException(APIException):
    """Request failed due to unauthorized access"""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Not authorized")
    default_code = "AUTH_REQUIRED"


class ForbiddenExceptionAPIException(APIException):
    """Request failed due to forbidden access"""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("Permission denied")
    default_code = "PERMISSION_DENIED"


class NotFoundExceptionAPIException(APIException):
    """Request failed due to not found"""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Not found")
    default_code = "RESOURCE_NOT_FOUND"


class BadRequestExceptionAPIException(APIException):
    """Request failed due to bad request"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Bad request")
    default_code = "VALIDATION_ERROR"


class ValidationErrorAPIException(APIException):
    """Request failed due to validation error"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Invalid parameters")
    default_code = "VALIDATION_ERROR"


class ThrottledAPIException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _("Request was throttled")
    default_code = "RATE_LIMIT_EXCEEDED"

    def __init__(self, wait=None, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        super().__init__(detail=detail, code=code)
        self.wait = wait


def exception_handler(exc, context):
    # pylint: disable=import-outside-toplevel
    from rest_framework.views import exception_handler as drf_exception_handler

    # if Django raises a validation error, let's say in .save method, it won't be handled by DRF
    # and end up raising a 500 Internal Error; So here we are converting Django's Validation errors into DRF's
    # validation errors
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            exc = DRFValidationError(detail=exc.message_dict)
        elif hasattr(exc, "message"):
            exc = DRFValidationError(detail=exc.message)
        elif hasattr(exc, "messages"):
            exc = DRFValidationError(detail=exc.messages)

    return drf_exception_handler(exc, context)
