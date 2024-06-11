from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.pagination import PageNumberPagination as DRFPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DRFPageNumberPagination):
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            data=OrderedDict(
                [
                    ("success", True),
                    ("code", status.HTTP_200_OK),
                    ("status", "Ok"),
                    ("message", _("Success")),
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            ),
            status=status.HTTP_200_OK,
        )
