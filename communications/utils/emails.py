import io
from collections import namedtuple
from smtplib import SMTPRecipientsRefused
from typing import List, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from sentry_sdk import capture_exception

User = get_user_model()

HTML_MIMETYPE = 'text/html'
File = namedtuple('File', 'mime_type ext')


class FileType:

    csv = File('text/csv', '.csv')
    gzip = File('application/gzip', '.gz')


def append_ext(file_name: str, ext: str) -> str:
    """
    appends `ext` at the end of name if already doesn't exist
    """
    return file_name if file_name.endswith(ext) else f'{file_name}{ext}'


# pylint: disable=too-many-arguments,invalid-name,protected-access
class Email(EmailMultiAlternatives):
    """
    Email Utility class to send all types of emails
    """

    def __init__(
            self, subject: str = '', body: str = '', to: Union[List[User], List[str]] = None,
            bcc: Union[List[User], List[str]] = None, cc: Union[List[User], List[str]] = None,
            from_email: str = settings.EMAIL_FROM, html_body: str = '', **kwargs
    ):

        self.invalid_users = set()

        to = self._validate_emails(to) if bool(to) and isinstance(to[0], str) else self._get_emails(to)
        bcc = self._validate_emails(bcc) if bool(bcc) and isinstance(bcc[0], str) else self._get_emails(bcc)
        cc = self._validate_emails(cc) if bool(cc) and isinstance(cc[0], str) else self._get_emails(cc)

        super().__init__(subject=subject, body=body, from_email=from_email, to=to, bcc=bcc, cc=cc, **kwargs)

        if html_body:
            self.attach_alternative(html_body, HTML_MIMETYPE)

    @classmethod
    def from_templates(
            cls, templates_path: str, context: dict, to: Union[List[User], List[str]] = None,
            bcc: Union[List[User], List[str]] = None, cc: Union[List[User], List[str]] = None,
            from_email: str = settings.EMAIL_FROM, **kwargs
    ) -> 'Email':
        """
        creates and returns an Email instance using templates and context
        """

        subject = render_to_string(f'{templates_path}/subject.txt', context)
        html_body = render_to_string(f'{templates_path}/body.html', context)
        text_body = render_to_string(f'{templates_path}/body.txt', context)

        return cls(
            subject=subject, body=text_body, to=to, bcc=bcc, cc=cc, from_email=from_email, html_body=html_body, **kwargs
        )

    # pylint: disable=inconsistent-return-statements
    def send(self, fail_silently=False, bulk=True) -> int:
        """
        Sends emails and returns number of emails sent
        - if bulk is True: Each recipient will receive an email addressed to him/her only
        - if bulk is False: Each recipient will receive an email addressed to all recipients
        """

        try:
            if bulk and len(self.recipients()) > 1:
                return self._send_bulk(fail_silently=fail_silently)
            return super().send(fail_silently=fail_silently)
        except SMTPRecipientsRefused as ex:
            capture_exception(ValueError(f"These {ex.recipients} emails were refused"))

    def with_file(self, file_name: str, file_buffer: io.StringIO, mime_type: str) -> 'Email':
        """
        attaches the given file with email and returns self
        """

        self.attach(file_name, file_buffer.read(), mime_type)
        return self

    def with_csv_file(self, file_name: str, file_buffer: io.StringIO) -> 'Email':
        """
        helper method to attach csv file with email
        """
        return self._with_a_file(file_name, file_buffer, FileType.csv)

    def with_gzip_file(self, file_name: str, file_buffer: io.StringIO) -> 'Email':
        """
        helper method to attach gzip file with email
        """
        return self._with_a_file(file_name, file_buffer, FileType.gzip)

    def clone(self) -> 'Email':
        """
        creates and returns a clone of self
        """
        clone_ = self.__class__(subject=self.subject, body=self.body, from_email=self.from_email,
                                connection=self.connection, headers=self.extra_headers, alternatives=self.alternatives,
                                reply_to=self.reply_to)

        clone_._override_recipients(self.to, self.bcc, self.cc)
        clone_.attachments = list(self.attachments)

        return clone_

    def _with_a_file(self, file_name: str, file_buffer: io.StringIO, file_type: File) -> 'Email':
        """
        takes file name, buffer and type and calls self.with_file with extension added and correct
        mime type
        """
        file_name = append_ext(file_name, file_type.ext)
        return self.with_file(file_name, file_buffer, file_type.mime_type)

    def _send_bulk(self, fail_silently=False) -> int:
        """
        sends a bulk email
        """
        messages = []

        for recipient in self.recipients():
            clone = self.clone()
            clone._override_recipients([], [], [])
            clone.to = [recipient]
            messages.append(clone)

        connection = self.get_connection(fail_silently=fail_silently)
        return connection.send_messages(messages)

    def _override_recipients(self, to: List[str], bcc: List[str], cc: List[str]) -> None:
        """
        overrides recipients with given values
        """
        self.to = list(to)
        self.bcc = list(bcc)
        self.cc = list(cc)

    def _validate_emails(self, addresses: List[str]) -> List[str]:
        """Takes in a list of email addresses and returns valid ones"""
        addresses = addresses or []
        return list({address for address in addresses if self.validate_mail(address)})

    def _get_emails(self, users: List[User]) -> List[str]:
        """
        accepts user lists and returns list of valid emails.
        Users without valid emails are saved in self.invalid_users
        """
        users = users or []
        valid_emails = set()

        for user in users:
            try:
                validate_email(user.email)
                valid_emails.add(user.email)
            except ValidationError:
                self.invalid_users.add(user)
        return list(valid_emails)

    @staticmethod
    def validate_mail(mail_id) -> bool:
        try:
            validate_email(mail_id)
            return True
        except ValidationError:
            return False
