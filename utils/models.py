import random
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def slug_generator() -> str:
    """
    Generates and returns a unique string of length 10-11
    Examples: 8273176561, 10153962259
    """
    return str(
        int(timezone.now().timestamp())
        + random.randint(  # nosec B311: random is not used for security/cryptographic purposes
            1, 9999999999
        )
    )  # NOSONAR


class AutoUpdateMixin:
    """
    By default, Django doesn't update `auto_now` field if `update_fields` is used while saving an object.
    This mixin makes sure that `auto_now` is updated along with `update_fields`

    Note:
        - It expects an `auto_now` field in the model named `updated_at` i.e.
            updated_at = models.DateTimeField(auto_now=True)

        - It doesn't have any effect on the Model.objects.update method (which also doesn't update `auto_save` field)
    """

    def save(self, *args, **kwargs):
        if kwargs.get("update_fields"):
            kwargs["update_fields"] = list(
                set(list(kwargs["update_fields"]) + ["updated_at"])
            )

        super().save(*args, **kwargs)


class TimeStampedModel(AutoUpdateMixin, models.Model):
    """
    An abstract base class model that provides self-updating ``created`` and ``modified`` fields.
    """

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    deleted_at = models.DateTimeField(_("deleted at"), blank=True, null=True)

    class Meta:
        abstract = True


class CustomModel(TimeStampedModel):
    """
    This model should be inherited by all models of the codebase.
    """

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)

    # User references
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_%(class)s_set",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_%(class)s_set",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="deleted_%(class)s_set",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True
