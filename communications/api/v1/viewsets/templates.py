from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from communications.api.v1.filters import TemplateFilter
from communications.api.v1.serializers import TemplateSerializer
from communications.models import Template
from utils.viewsets import ModelViewSet


class TemplateViewSet(ModelViewSet):
    serializer_class = TemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TemplateFilter
    search_fields = [
        "uuid",
        "name",
    ]

    def get_queryset(self):
        self.queryset = Template.objects.filter(
            organisation=self.request.user.organisation,
            business_unit=self.request.user.business_unit,
        )
        return super().get_queryset()
