from pydoc import locate
from typing import Union

from celery import shared_task
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from utils import logger

User = get_user_model()


# pylint: disable=too-many-arguments
@shared_task(ignore_result=True)
def send_csv_email(
    pks: list,
    columns: list,
    generator_class_import_path: str,
    model_class_label: str,
    user_id: Union[int, str],
    fail_silently: bool = True,
):
    """
    Asynchronous task to generate a CSV file and send it via email.

    This task is used by CSVFileOrEmailModelMixin to initiate CSV creation. It takes a list of primary keys (pks),
    uses them to fetch the corresponding objects from a specified model, generates a CSV file containing data from
    these objects, and then sends this CSV file as an email to the specified user.

    Parameters:
    pks (list): A list of primary keys of objects that should be included in the CSV file.
    columns (list): A list of column names to include in the CSV file.
    generator_class_import_path (str): The import path to the class responsible for generating the CSV file.
                                       This class must implement a method called 'initialize_instance' and
                                       'generate_csv_and_send_email'.
    model_class_label (str): The label of the model (in the format 'app_label.model_name') from which to fetch data
                             for the CSV file.
    user_id (Union[int, str]): The id of the user who should receive the email.
    fail_silently (bool): Determines whether to raise an exception if the user doesn't exist. If True, the function
                          will log an error and continue execution. If False, the function will raise an
                          ObjectDoesNotExist exception.

    Returns:
    None

    Raises:
    ObjectDoesNotExist: If a user with the specified user_id doesn't exist and fail_silently is False.
    """
    user_model = get_user_model()
    csv_generator_class = locate(generator_class_import_path)
    model = apps.get_model(model_class_label)
    queryset = model.objects.filter(pk__in=pks)
    instance = csv_generator_class.initialize_instance(model=model, queryset=queryset)
    try:
        user = user_model.objects.get(pk=user_id)
        instance.generate_csv_and_send_email(queryset, columns, user)
    except ObjectDoesNotExist as e:
        logger.info("Sending CSV through email failed because user with id %s doesn't exist.", user_id)
        if not fail_silently:
            raise e
