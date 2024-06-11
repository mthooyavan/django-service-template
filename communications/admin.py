from django.contrib import admin

from communications import models
from utils.admin import CustomModelAdmin, ReadOnlyMixin


@admin.register(models.CommunicationLog)
class CommunicationLogAdmin(ReadOnlyMixin, CustomModelAdmin):
    list_display = (
        "user",
        "communication_type",
        "client_notification_template_name",
        "sender_address",
        "recipient_address",
        "is_log_only",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "user",
        "client_notification_template_name",
        "sender_address",
        "communication_type",
        "is_log_only",
    )
    search_fields = (
        "client_notification_template_name",
        "recipient_address",
    )


@admin.register(models.Template)
class TemplateAdmin(CustomModelAdmin):
    list_display = (
        "uuid",
        "name",
        "language",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "language",
    )
    search_fields = (
        "uuid",
        "name",
    )
    readonly_fields = ("uuid",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "name",
                    "language",
                    "content",
                )
            },
        ),
    )
    ordering = ("name",)


@admin.register(models.Gateway)
class GatewayAdmin(CustomModelAdmin):
    list_display = (
        "uuid",
        "name",
        "type",
        "external_unique_id",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "type",
    )
    search_fields = (
        "uuid",
        "name",
    )
    readonly_fields = ("uuid",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                ),
            },
        ),
        (
            "Gateway Details",
            {
                "fields": (
                    "name",
                    "type",
                    "external_unique_id",
                ),
            },
        ),
        (
            "Authentication",
            {
                "fields": (
                    "auth_type",
                    "auth_context",
                ),
            },
        ),
        (
            "Configuration",
            {
                "fields": (
                    "api_url",
                    "headers",
                    "body_template",
                    "context",
                )
            },
        ),
    )
    ordering = ("name",)
