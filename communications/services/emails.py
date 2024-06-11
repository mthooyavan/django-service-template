# pylint:disable=too-many-arguments
from typing import List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model

from communications.models import CommunicationLog
from communications.utils import Email

User = get_user_model()


class EmailService:
    """
    This service acts as an abstraction layer between the application and the emailing service (Amazon SES, as of when
    this comment is written). The service also implicitly takes care of creating outbound email logs when messages
    are sent out.
    """

    def __init__(
        self,
        templates_path,
        to_addresses: List[User] | List[str],
        from_address: str = settings.EMAIL_FROM,
        context: dict = None,
        user: User = None,
    ):
        self.templates_path = templates_path
        self.to_addresses = to_addresses
        self.from_address = from_address
        self.context = context or {}
        self.email: Optional[Email] = None
        self.user = user

    def compile(self):
        self.email = Email.from_templates(
            self.templates_path,
            self.context,
            to=self.to_addresses,
            from_email=self.from_address,
        )

    def send(self, raise_exc: bool = True):
        self.compile()
        self.email.send(fail_silently=not raise_exc)

    def log_only(self) -> "CommunicationLog":
        """
        Only logs the email but does not send it out
        """
        self.compile()
        user = self.user if isinstance(self.user, User) else None
        return CommunicationLog.objects.create(
            user=user.id if user else None,
            content=f"{self.email.subject}\n\n{self.email.body}",
            sender_address=self.from_address,
            recipient_address=[self.to_addresses],
            is_log_only=True,
            client_notification_template_name=self.templates_path,
            communication_type=CommunicationLog.CommunicationTypes.EMAIL,
        )

    def send_and_log(self, raise_exc: bool = True) -> Optional["CommunicationLog"]:
        self.compile()
        exc = None
        user = self.user if isinstance(self.user, User) else None
        log = CommunicationLog(
            user=user.id if user else None,
            content=f"{self.email.subject}\n\n{self.email.body}",
            sender_address=self.from_address,
            recipient_address=[self.to_addresses],
            client_notification_template_name=self.templates_path,
            communication_type=CommunicationLog.CommunicationTypes.EMAIL,
        )
        try:
            self.send(
                raise_exc=raise_exc,
            )
        except Exception as exc_:  # pylint: disable=broad-except
            exc = exc_
            log.error_response = str(exc)
        log.save()
        if raise_exc and exc:
            raise exc
        return log

    # pylint: disable=unnecessary-comprehension
    def send_with_bulk_context_and_log(
        self, raise_exc: bool = True
    ) -> List["CommunicationLog"]:
        logs = []
        for email in self.to_addresses:
            if self.context.get(email):
                service = EmailService(
                    context=self.context[email],
                    to_addresses=[email],
                    templates_path=self.templates_path,
                )
                logs.append(service.send_and_log(raise_exc))
        return logs
