from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from utils.validations import validate_email_template


# pylint: disable=abstract-method
class NotificationValidationSerializer(serializers.Serializer):

    template = serializers.CharField()
    emails = serializers.ListSerializer(child=serializers.EmailField())
    from_address = serializers.EmailField(required=False)
    context = serializers.DictField(required=False)

    def validate_template(self, template):
        validated_template = validate_email_template(template)
        if validated_template:
            return validated_template
        raise ValidationError({"error": f"Template name '{template}' is not valid"})
