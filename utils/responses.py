from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import status as http_status


def get_status_message(status_code):
    status_messages = {
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        429: "Too Many Requests",
        500: "Internal Server Error",
        503: "Service Unavailable",
    }
    return status_messages.get(status_code, "Ok")


def get_error_message(status_code):
    error_messages = {
        400: "VALIDATION_ERROR",
        401: "AUTH_FAILED",
        402: "PAYMENT_REQUIRED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    return error_messages.get(status_code, "INTERNAL_SERVER_ERROR")


def get_message(status_code):
    messages = {
        201: _("Created Successfully"),
        204: _("Deleted Successfully"),
        400: _("Bad Request"),
        401: _("Unauthorized Access"),
        402: _("Credits are not available"),
        403: _("Access Restricted"),
        404: _("Not Found"),
        405: _("Invalid Request Method"),
        429: _("Too Many Requests, Please Try Again Later"),
        500: _("Internal Server Error, Please Try Again Later"),
        503: _("Service Unavailable, Please Try Again Later"),
    }
    return messages.get(status_code, _("Success"))


def success_response(
    headers: dict = None,
    message: str = _("Success"),
    data: dict = None,
    status_code: int = http_status.HTTP_200_OK,
):
    response = JsonResponse(
        data={
            "success": True,
            "code": status_code,
            "status": get_status_message(status_code),
            "message": message,
            "data": data,
        },
        status=status_code,
    )
    if headers:
        response.headers.update(headers)

    return response


def error_response(
    error: dict,
    headers: dict = None,
    message: str = None,
    status_code: int = http_status.HTTP_400_BAD_REQUEST,
):
    response = JsonResponse(
        data={
            "success": False,
            "code": status_code,
            "status": get_status_message(status_code),
            "error": get_error_message(status_code),
            "message": message or get_message(status_code),
            "data": {"error": error},
        },
        status=status_code,
    )
    if headers:
        response.headers.update(headers)

    return response
