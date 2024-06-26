from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils import Choices

from utils.models import TimeStampedModel

CommunicationTypes = Choices(
    ("SMS", "Text message"),
    ("EMAIL", "Email"),
    ("WEBHOOK", "Webhook"),
    ("TEAMS", "Teams"),
)

User = get_user_model()


class CommunicationLog(TimeStampedModel):
    CommunicationTypes = CommunicationTypes

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="communication_logs",
    )
    client_notification_template_name = models.CharField(blank=True, max_length=225)
    content = models.TextField(blank=True)
    sender_address = models.CharField(max_length=250)
    recipient_address = ArrayField(models.EmailField())
    communication_type = models.CharField(max_length=32, choices=CommunicationTypes)
    is_log_only = models.BooleanField(
        default=False,
        help_text="Indicates whether this is only a log record and message was actually sent",
    )
    error_response = models.TextField(
        blank=True, help_text="Set when upstream provider returns an error"
    )

    def __str__(self):
        return f"Communication log for {self.user}"
