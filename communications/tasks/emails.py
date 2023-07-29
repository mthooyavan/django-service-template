from celery import shared_task
from django.contrib.auth import get_user_model

from communications.services import EmailService
from utils.users import notifications_user

User = get_user_model()


@shared_task(ignore_result=True)
def send_notifications(data, user: User = notifications_user):
    email_service = EmailService(
        templates_path=data["template"],
        to_addresses=data["emails"],
        context=data.get("context"),
        user=user,
    )
    if data.get("from_address"):
        email_service.from_address = data["from_address"]
    email_service.send_with_bulk_context_and_log()
