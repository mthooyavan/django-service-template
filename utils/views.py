from rest_framework.views import APIView as DefaultAPIView

from backend_service.exceptions import (
    ForbiddenExceptionAPIException,
    MethodNotAllowedAPIException,
    NotAuthorizedAPIException,
    ThrottledAPIException,
)


class APIView(DefaultAPIView):
    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        raise MethodNotAllowedAPIException(f"Method '{request.method}' not allowed")

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if request.authenticators and not request.successful_authenticator:
            raise NotAuthorizedAPIException
        raise ForbiddenExceptionAPIException

    def throttled(self, request, wait):
        """
        If request is throttled, determine what kind of exception to raise.
        """
        raise ThrottledAPIException(wait=wait)
