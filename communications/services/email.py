from typing import List, Union

from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
from django_ses import SESBackend as RealEmailBackend


class EmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently: bool = ..., **kwargs) -> None:
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.fail_silently = fail_silently
        self.kwargs = kwargs
        self.allow_sending_patterns = ["test", "example.com"]
        self.email_backend = None
        self.console_backend = None

    def send_messages(self, email_messages):
        for message in email_messages:
            backend = self._get_backend(message)
            backend.send_messages([message])

    def _get_backend(self, email) -> Union[ConsoleEmailBackend, RealEmailBackend]:
        def address_contains(pattern, address: Union[str, List[str]]):
            if isinstance(address, list):
                return all(map(lambda a: pattern in a, address))
            elif isinstance(address, str):
                return pattern in address
            else:
                raise Exception(
                    f"Unknown address type {type(address)} of {address}"
                )  # pylint: disable=broad-exception-raised

        contains_pattern = map(
            lambda pattern: address_contains(pattern, email.to),
            self.allow_sending_patterns,
        )
        contains_pattern = any(contains_pattern)

        # create and cache for further usage
        if contains_pattern:
            if not self.email_backend:
                self.email_backend = RealEmailBackend(self.fail_silently, **self.kwargs)
                self.email_backend.open()
            return self.email_backend
        else:
            if not self.console_backend:
                self.console_backend = ConsoleEmailBackend(
                    self.fail_silently, **self.kwargs
                )
                self.console_backend.open()
            return self.console_backend
