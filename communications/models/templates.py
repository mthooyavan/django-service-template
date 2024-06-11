import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.enums import LANGUAGES
from utils.models import CustomModel


class Template(CustomModel):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
    )
    name = models.CharField(
        _("name"),
        max_length=100,
        db_index=True,
        help_text=_("name of the invitee"),
    )
    language = models.CharField(
        _("language"),
        choices=LANGUAGES,
        blank=True,
        max_length=8,
        help_text=_("language for the invitee"),
    )
    content = models.TextField(
        _("content"),
        help_text=_("content of the invite"),
    )

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")

    def __str__(self):
        return self.name
