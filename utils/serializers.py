import csv
import io
from typing import List

from django.db.models import QuerySet

from utils.file import CSVFileCompressionMixin
from utils.tasks import send_csv_email


class CSVTooLarge(Exception):
    """
    Custom exception class to handle situations where the number of rows required to
    generate the CSV exceeds the set limit. When this exception is raised, it signifies
    that the CSV is too large to be created instantly and thus needs to be handled
    asynchronously, likely using a background task.
    """


class CSVFileOrEmailModelMixin(CSVFileCompressionMixin):
    """
    This mixin class is used by other classes that generate CSV files from data in a database.
    It provides functionality to either directly generate a CSV file if the data is within a
    specified limit or offload this task to a celery task when the data size exceeds the limit.

    Attributes:
        MAX_INLINE_LIMIT (int): The maximum number of rows that can be processed
                                immediately for CSV generation.
        LARGE_CSV_MSG (str): A user-friendly message displayed when the data size is too large.
        EMAIL_CSV_MSG (str): A user-friendly message displayed when the CSV is emailed.
        send_email (bool): A flag to indicate if an email needs to be sent for large data.
        email_templates_path (str): The path where email templates are stored.
        csv_file_name (str): The name of the generated CSV file.
    """

    # Maximum number of rows that we're willing to generate synchronously
    MAX_INLINE_LIMIT = 500

    # Message to display when the requested CSV is too large to generate immediately
    LARGE_CSV_MSG = 'The requested file is too large to download.'

    # Message to display when the CSV is going to be emailed to the user
    EMAIL_CSV_MSG = 'You will receive an email with the report once completed.'

    # Flag indicating whether to send email or not
    send_email = True

    # Path to the email templates for CSV download
    email_templates_path = 'emails/csv_download'

    # Filename of the generated CSV file
    csv_file_name = None

    @classmethod
    def initialize_instance(cls, *args, **kwargs):
        """
        Class method used to initialize an instance of a class that inherits from this
        mixin. It is intended to be called by the `send_csv_email` Celery task in order
        to prepare the class instance that is required for generating the CSV file.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.

        Returns:
            An instance of the class that called this method.
        """
        return cls(*args, **kwargs)

    def generate_csv(self, request, queryset) -> io.StringIO:
        """
        This method attempts to generate a CSV file from the queryset. If the queryset is
        small (i.e., <= MAX_INLINE_LIMIT), it generates the CSV file immediately. If the
        queryset is large, it schedules a Celery task to generate the CSV file and, if
        applicable, email it to the user.

        Args:
            request: The client request to generate a CSV file.
            queryset: A Django QuerySet from which the CSV data will be generated.

        Returns:
            A StringIO object containing CSV data if the queryset is small.

        Raises:
            CSVTooLarge: An error indicating the CSV data was too large to be generated immediately.
        """
        if not isinstance(queryset, QuerySet):
            model = self.get_csv_model()
            queryset = model.objects.filter(pk__in=(o.pk for o in queryset))

        columns = self.get_columns(request, queryset)
        if queryset[:self.MAX_INLINE_LIMIT + 1].count() <= self.MAX_INLINE_LIMIT:
            return self.get_buffer(queryset, columns)

        msg = self.LARGE_CSV_MSG
        if self.send_email:
            msg = f'{self.LARGE_CSV_MSG} {self.EMAIL_CSV_MSG}'
            self.initialize_email_task(request, queryset, columns)
        raise CSVTooLarge(msg)

    def get_buffer(self, queryset, columns) -> io.StringIO:
        """
        This method should be implemented by the child classes. It is intended to return a
        CSV buffer containing data from the provided queryset and columns.

        Args:
            queryset: A Django QuerySet that provides data to generate CSV.
            columns: A list of column names to be included in the CSV.

        Returns:
            A StringIO object containing CSV data.

        Raises:
            NotImplementedError: An error indicating the method needs to be implemented by the child classes.
        """
        raise NotImplementedError

    def get_columns(self, request, queryset) -> List[str]:
        """
        Abstract method that needs to be implemented by any class that inherits from this
        mixin. This method should return a list of column names to be included in the
        generated CSV file.

        Args:
            request: The client request to generate a CSV file.
            queryset: A Django QuerySet from which the CSV data will be generated.

        Returns:
            A list of column names to be included in the CSV file.

        Raises:
            NotImplementedError: An error indicating the method needs to be implemented by the child classes.
        """
        raise NotImplementedError

    def get_csv_too_large_buffer(self) -> io.StringIO:
        """
        This method is used when the CSV is too large to be created immediately. It
        returns a CSV buffer with a single cell containing a message notifying the user
        that their CSV request was too large and will be emailed to them once the file is
        ready.

        Returns:
            A StringIO object containing a single CSV cell with the notification message.
        """
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, [f'{self.LARGE_CSV_MSG} {self.EMAIL_CSV_MSG}'])
        writer.writeheader()
        buffer.seek(0)
        return buffer

    def generate_csv_and_send_email(self, queryset, columns, user):
        """
        This method generates a CSV file and emails it to the user. It first creates a
        CSV buffer from the queryset and columns. Then it compresses the buffer if the size
        is too large. It then constructs an email with the CSV file as an attachment and sends
        it to the user.

        Args:
            queryset: A Django QuerySet that provides data to generate CSV.
            columns: A list of column names to be included in the CSV.
            user: The user to whom the email with the CSV file will be sent.
        """
        # pylint: disable=import-outside-toplevel
        from communications.utils import Email, FileType, append_ext
        buffer = self.get_buffer(queryset, columns)
        compressed, buffer = self.conditional_compress(buffer)
        model = self.get_csv_model()
        context = {'user': user, 'request_for': model._meta.verbose_name_plural.capitalize()}
        email = Email.from_templates(self.email_templates_path, context, [user])
        csv_file_name = self.get_csv_file_name()
        if compressed:
            email.with_gzip_file(append_ext(csv_file_name, FileType.csv.ext), buffer).send()
        else:
            email.with_csv_file(csv_file_name, buffer).send()

    def initialize_email_task(self, request, queryset, columns):
        """
        This method schedules a Celery task to generate and email a CSV file to the user.
        It first prepares the necessary information for the task, including the class
        path, the model, and primary keys from the queryset. It then sends this information
        to the Celery task.

        Args:
            request: The client request to generate a CSV file.
            queryset: A Django QuerySet that provides data to generate CSV.
            columns: A list of column names to be included in the CSV.
        """
        generator_class_import_path = f'{self.__class__.__module__}.{self.__class__.__qualname__}'
        model_class_label = self.get_csv_model()._meta.label
        pks = list(queryset.values_list('pk', flat=True))
        send_csv_email.delay(pks, columns, generator_class_import_path, model_class_label, request.user.pk)

    def get_csv_model(self):
        """
        This method is intended to return the model class that provides data for the CSV.
        It should be implemented in the child classes. By default, it returns None.

        Returns:
            The model class providing data for CSV.
        """
        return getattr(self, 'model', None)

    def get_csv_file_name(self) -> str:
        """
        This method provides the filename to be used for the generated CSV file. If a
        filename is not explicitly set in csv_file_name, it generates one from the model
        verbose name.

        Returns:
            A string representing the filename for the generated CSV file.
        """
        return self.csv_file_name or self.get_csv_model()._meta.verbose_name_plural
