from django.conf import settings
from django.utils.translation import gettext_lazy as _

ENV = settings.ENV

# File Handling
FILE_STORAGE_PATH = ENV.str("FILE_STORAGE_PATH", default="/code/data")
AUDIO_STORAGE_PATH = ENV.str("MEDIA_STORAGE_PATH", default="/code/data/audio")
DATA_UPLOAD_MAX_MEMORY_SIZE = ENV.int(
    "DATA_UPLOAD_MAX_MEMORY_SIZE", default=104857600
)  # 100 MB
DISABLE_ATTACHMENT_FILE_SIZE = ENV.int(
    "DISABLE_ATTACHMENT_FILE_SIZE", default=20971520
)  # 20 MB
# max limit on file size in bytes after which file must be compressed
ENFORCE_COMPRESSION_FILE_SIZE = ENV.int(
    "ENFORCE_COMPRESSION_FILE_SIZE", default=5242880
)  # 5 MB

# Model constants
# ------------------------------------------------------------------------------
GATEWAY_MODEL = "communications.Gateway"

# Admin constants
BASIC_INFO = _("Basic Info")

# Max bulk invite limit
MAX_BULK_INVITE_LIMIT = ENV.int("MAX_BULK_INVITE_LIMIT", default=100)

# Swagger constants
REQUEST_WAS_SUCCESSFUL_DESCRIPTION = _("The request was successful.")
SUCCESS_FIELD_DESCRIPTION = _("True if the request was successful, False otherwise")
STATUS_CODE_FIELD_DESCRIPTION = _("HTTP status code")
STATUS_TEXT_FIELD_DESCRIPTION = _("HTTP status text")
ERROR_CODE_FIELD_DESCRIPTION = _("Error code")
ERROR_MESSAGE_FIELD_DESCRIPTION = _("Error message")
ERROR_FIELD_DESCRIPTION = _("Error detail")
THROTTLED_DESCRIPTION = _("Request was throttled")
JSON_FORMAT = "application/json"

# Model constants
VERBOSE_CREATED_AT = "created at"
VERBOSE_UPDATED_AT = "updated at"
VERBOSE_DELETED_AT = "deleted at"
VERBOSE_CREATED_BY = "created by"
VERBOSE_UPDATED_BY = "updated by"
VERBOSE_DELETED_BY = "deleted by"
RELATED_NAME_CREATED_BY = "created_%(class)s_set"
RELATED_NAME_UPDATED_BY = "updated_%(class)s_set"
RELATED_NAME_DELETED_BY = "deleted_%(class)s_set"

# Misc constants
INVALID_PASSWORD_RESET_LINK = _("Invalid password reset link")
STANDARD_SCOPE = "standard"
AUTHENTICATION_SCOPE = "auth"
CLIENT_THROTTLE_SCOPE = "client"

# Cache configuration constants
ONE_DAY = 24 * 60 * 60
ONE_HOUR = 60 * 60

# Logging constants
AUTHENTICATION_ERROR_LOG = "AuthenticationError: %s"

# error messages
# ------------------------------------------------------------------------------
INCORRECT_UUID_TYPE = _("Incorrect type. Expected UUID.")
PERMISSION_REQUIRED = _("Permission is required.")
INVALID_PERMISSION = _("Invalid permission.")
USER_REQUIRED = _("User is required.")
USER_NOT_FOUND = _("User not found.")

# admin page text
# ------------------------------------------------------------------------------
BASIC_INFORMATION = _("Basic Information")
META_INFORMATION = _("Meta Information")
