import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

User = get_user_model()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Use this management command to create a superuser from env variables.

    If the superuser account already exists, print a relevant statement
    on the console, instead of raising an error (prevents the flow of `start` script on runtime)
    """

    def handle(self, *args, **options):
        email = settings.SUPERUSER_EMAIL
        password = settings.SUPERUSER_PASSWORD

        full_name = settings.SUPERUSER_FULL_NAME
        parts = full_name.split(" ")
        first_name = " ".join(parts[:-1])
        last_name = ""
        if len(parts) > 1:
            last_name = full_name.split(" ")[-1]

        if User.objects.filter(email=email).exists():
            logger.warning("An superuser account with this username already exists.")
            return

        try:
            user = User.objects.create_superuser(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password(password)
            user.save(update_fields=["password"])
        except IntegrityError as e:
            logger.warning("Something went wrong while creating the superuser account.")
            logger.error("Error: %s", e)
            return
        else:
            logger.info("Superuser created successfully.")
            return
