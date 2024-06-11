import django_filters

from communications.models import Template


class TemplateFilter(django_filters.FilterSet):
    class Meta:
        model = Template
        fields = ["language"]
