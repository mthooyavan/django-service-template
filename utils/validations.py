from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from communications.utils import Email


def validate_email_template(template):
    absolute_template = f'emails/{template}'
    try:
        get_template(absolute_template)
        return None
    except TemplateDoesNotExist:
        return None
    except IsADirectoryError:
        return absolute_template


def extract_valid_emails(emails):
    valid_emails = []
    for email in emails:
        if Email.validate_mail(email):
            valid_emails.append(email)

    return valid_emails


def validated_email(email):
    if Email.validate_mail(email):
        return email

    return None
