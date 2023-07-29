from django.contrib import admin

from communications import models


@admin.register(models.CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'organisation',
        'communication_type',
        'client_notification_template_name',
        'sender_address',
        'recipient_address',
        'error_response',
        'is_log_only',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'user',
        'organisation',
        'client_notification_template_name',
        'sender_address',
        'communication_type',
        'is_log_only',
    )
    search_fields = (
        'client_notification_template_name',
        'recipient_address',
    )
