import json

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.enums import AUTH_TYPE_CHOICES, GATEWAY_TYPES, HTTP_METHODS
from utils.models import CustomModel


class Gateway(CustomModel):
    external_unique_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text=_("External unique ID for the gateway."),
    )
    name = models.CharField(max_length=255, db_index=True, help_text=_("Name of the gateway."))
    type = models.CharField(max_length=32, choices=GATEWAY_TYPES)
    auth_type = models.CharField(max_length=32, choices=AUTH_TYPE_CHOICES)
    auth_context = models.JSONField(
        blank=True,
        default=dict,
        help_text=_(
            "Authentication details like API key, username:password for Basic Auth, token, etc."
        ),
    )
    api_url = models.URLField(
        max_length=1024, help_text=_("API URL for the gateway API.")
    )
    request_method = models.CharField(
        choices=HTTP_METHODS,
        max_length=10,
        default=HTTP_METHODS.POST,
        help_text=_("HTTP method for requests."),
    )
    headers = models.JSONField(
        blank=True, default=dict, help_text=_("Default headers for requests.")
    )
    body_template = models.JSONField(
        blank=True, default=dict, help_text=_("Template for the request body.")
    )
    params_template = models.JSONField(
        blank=True, default=dict, help_text=_("Template for URL parameters.")
    )
    success_response_codes = ArrayField(
        models.PositiveSmallIntegerField(),
        blank=True,
        default=list,
        help_text=_("List of success response codes."),
    )
    response_path_to_message = models.JSONField(
        max_length=255,
        blank=True,
        default=dict,
        help_text=_(
            "Dot notation path in the response JSON to find the actual message or result (e.g., 'data.result')."
        ),
    )
    context = models.JSONField(
        blank=True,
        default=dict,
        help_text=_("Context for the gateway like variables, etc."),
    )

    class Meta:
        verbose_name = _("Gateway")
        verbose_name_plural = _("Gateways")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.type}"

    def get_body_template(self):
        body_template = {}
        if self.body_template:
            body_template = self.body_template
        elif self.type == GATEWAY_TYPES.whatsapp:
            body_template = {
                "messaging_product": "whatsapp",
                "to": "{{mobile_number}}",
                "type": "template",
                "template": {
                    "name": "{{template_name}}",
                    "language": {"code": "{{language}}"},
                },
            }
        return json.dumps(body_template)

    def get_header_template(self):
        headers = {}
        if self.headers:
            headers = self.headers
        elif self.type == GATEWAY_TYPES.whatsapp:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {{token}}",
            }
        return json.dumps(headers)
