from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from communications.models import Template


class TemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Template
        fields = (
            "uuid",
            "name",
            "language",
            "content",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["organisation"] = self.context["request"].user.organisation
        attrs["business_unit"] = self.context["request"].user.business_unit
        attrs["created_by"] = self.context["request"].user
        return attrs
