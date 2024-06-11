from rest_framework.viewsets import GenericViewSet as DefaultGenericViewSet

from backend_service.exceptions import (
    ForbiddenExceptionAPIException,
    MethodNotAllowedAPIException,
    NotAuthorizedAPIException,
)
from utils import mixins


class GenericViewSet(DefaultGenericViewSet):
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


class ReadOnlyModelViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """


class ModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """


class ExcludingListModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Viewset for retrieving, creating, updating, and deleting Connections.
    """
