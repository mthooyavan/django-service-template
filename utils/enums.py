from django.utils.translation import gettext_lazy as _
from model_utils import Choices

LANGUAGES = Choices(
    ("ar", _("Arabic")),
    ("de", _("German")),
    ("en", _("English")),
    ("es", _("Spanish")),
    ("fr", _("French")),
    ("hi", _("Hindi")),
    ("kn", _("Kannada")),
    ("ta", _("Tamil")),
    ("te", _("Telugu")),
)

AUTH_TYPE_CHOICES = Choices(
    ("none", _("None")),
    ("api_key", _("API Key")),
    ("bearer_token", _("Bearer Token")),
    ("basic_auth", _("Basic Auth")),
    ("oauth2", _("OAuth 2.0")),
)

HTTP_METHODS = Choices(
    ("GET", _("GET")),
    ("POST", _("POST")),
    ("PUT", _("PUT")),
    ("PATCH", _("PATCH")),
)

GATEWAY_TYPES = Choices(
    ("sms", _("SMS")),
    ("email", _("Email")),
    ("whatsapp", _("WhatsApp")),
)
