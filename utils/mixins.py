from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.mixins import CreateModelMixin as DefaultCreateModelMixin
from rest_framework.mixins import DestroyModelMixin as DefaultDestroyModelMixin
from rest_framework.mixins import ListModelMixin as DefaultListModelMixin
from rest_framework.mixins import RetrieveModelMixin as DefaultRetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin as DefaultUpdateModelMixin

from backend_service.pagination import PageNumberPagination
from utils.responses import success_response


class CSRFExemptMixin:
    """
    Exempts the view from CSRF requirements.

    :param object: The object to be exempted from CSRF requirements.

    :return: The CSRF exempted object.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Dispatch method to exempt the view from CSRF requirements.

        :param args: Arguments to be passed to the dispatch method.
        :param kwargs: Keyword arguments to be passed to the dispatch method.

        :return: The dispatch method.
        """
        return super().dispatch(*args, **kwargs)


class RetrieveModelMixin(DefaultRetrieveModelMixin):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve method to retrieve a model instance.

        :param request: The request object.
        :param args: Arguments to be passed to the retrieve method.
        :param kwargs: Keyword arguments to be passed to the retrieve method.

        :return: The retrieve method.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


class ListModelMixin(DefaultListModelMixin):
    """
    List a queryset.
    """

    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class CreateModelMixin(DefaultCreateModelMixin):
    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        bulk = kwargs.pop("bulk", False)
        serializer = self.get_serializer(
            data=request.data, many=bulk, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return success_response(
            data=serializer.data, status_code=status.HTTP_201_CREATED, headers=headers
        )


class UpdateModelMixin(DefaultUpdateModelMixin):
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}  # pylint: disable=protected-access

        return success_response(data=serializer.data)


class DestroyModelMixin(DefaultDestroyModelMixin):
    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            message=_("Deleted successfully"), status_code=status.HTTP_204_NO_CONTENT
        )
