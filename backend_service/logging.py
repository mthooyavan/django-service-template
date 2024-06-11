import logging
import re
import threading

thread_local_storage = threading.local()


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to mask sensitive data in log messages.
    """

    number_of_chars_to_mask = 8
    # Define a regular expression pattern to identify sensitive data
    sensitive_patterns = [
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN format
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ),  # Email format
        re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),  # Credit card number format
        re.compile(
            r"\b(?:male|female|other|non-binary|transgender)\b", re.IGNORECASE
        ),  # Gender
        re.compile(r"\b\d{10}\b"),  # Mobile number (10 digits format)
        re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),  # IP address format
        re.compile(r"\b\d{2}/\d{2}/\d{4}\b"),  # Date of birth format (MM/DD/YYYY)
        re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),  # Date format (YYYY-MM-DD)
        re.compile(r"\b\d{5}(-\d{4})?\b"),  # ZIP/postal code format
    ]

    def _mask_sensitive_data(self, match):
        """
        Custom function to replace sensitive data with masked version, keeping the first and last characters.
        """
        text = match.group()
        if len(text) > 2:
            return text[0] + "*" * self.number_of_chars_to_mask + text[-1]
        else:
            return "*" * self.number_of_chars_to_mask

    def filter(self, record):
        record.org_id = getattr(thread_local_storage, "org_id", "System")
        record.user_id = getattr(thread_local_storage, "user_id", "System")
        record.correlation_id = getattr(
            thread_local_storage, "correlation_id", "Unknown"
        )
        if record.args:
            record.msg = record.msg % record.args
            record.args = ()

        if isinstance(record.msg, str):
            message = record.msg
            for pattern in self.sensitive_patterns:
                message = pattern.sub(self._mask_sensitive_data, message)
            record.msg = message

        return True
