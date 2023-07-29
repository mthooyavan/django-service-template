import csv
import io
import os

from django.contrib import admin, messages
from django.contrib.admin.utils import lookup_field
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.utils import timezone

from utils.file import file_size
from utils.serializers import CSVFileOrEmailModelMixin, CSVTooLarge


class AutoCompleteMixin:
    """
    Mixin that enables autocomplete functionality on related fields in the Django admin.
    It currently supports only ForeignKey and OneToOneField fields. The autocomplete
    functionality for fields listed in skip_autocomplete_fields will be skipped.
    AutoCompleteMixin must be included before ModelAdmin, otherwise it won't work.

    Attributes:
    RELATED_FIELD_TYPES: Tuple that holds the types of fields that support autocomplete.
    GENERIC_FOREIGNKEY_FIELDS: Tuple that holds the field names which are of type GenericForeignKey.
    Autocomplete is always skipped for these fields. skip_autocomplete_fields: Tuple that holds the field names for
    which autocomplete needs to be skipped. This can be overridden in the child class.
    related_fields: List that will hold the related fields (ForeignKey and OneToOneField) of the model, for which
    autocomplete needs to be enabled.
    """

    RELATED_FIELD_TYPES = ("ForeignKey", "OneToOneField")

    # Generic ForeignKey Fields always skip for autocomplete, since auto-completing them causes errors.
    GENERIC_FOREIGNKEY_FIELDS = ("content_object", "content_type", "object_id")
    skip_autocomplete_fields = ()

    def __init__(self, model, admin_site):
        """
        Initialize the mixin and set the related fields for autocomplete.

        Args:
            model: Model object for which autocomplete should be set up.
            admin_site: Current admin site object.
        """
        super().__init__(model, admin_site)
        fields = [
            field
            for field in self.model._meta.get_fields()
            if field.name not in self.GENERIC_FOREIGNKEY_FIELDS
        ]
        self.related_fields = [
            field.name
            for field in fields
            if field.get_internal_type() in self.RELATED_FIELD_TYPES
        ]
        for field in self.skip_autocomplete_fields:
            if field in self.autocomplete_fields:
                raise ValueError(
                    f"autocomplete_fields and skip_autocomplete_fields cannot contain same field: {field}"
                )

    def get_autocomplete_fields(self, request):
        """
        Return the fields for which autocomplete is enabled.

        Args:
            request: Current HTTP request.

        Returns:
            A set of fields for which autocomplete is enabled.
        """
        autocomplete_fields = set(self.related_fields)
        autocomplete_fields.update(self.autocomplete_fields)
        if self.skip_autocomplete_fields:
            return autocomplete_fields - set(self.skip_autocomplete_fields)
        return autocomplete_fields


class CustomModelAdmin(AutoCompleteMixin, admin.ModelAdmin):
    """
    A CustomModelAdmin that extends from the AutoCompleteMixin and Django's ModelAdmin.
    It ensures all the models inherit the global behaviors defined in this class.
    The deleted records can be restored via Django's actions dropdown.

    Attributes:
    readonly_fields: Tuple that holds the fields which are read-only in the Django admin.
    actions: List that holds the custom actions defined for the model in the Django admin.
    """

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "created_by",
        "updated_by",
        "deleted_by",
    )

    actions = [
        "restore_selected_records",
    ]

    def restore_selected_records(self, request, queryset):
        """
        Restore the selected records that are marked as deleted.

        Args:
            request: Current HTTP request.
            queryset: The selected rows in the Django admin.
        """
        count = queryset.exclude(deleted_by=None).count()
        queryset.exclude(deleted_by=None).update(
            deleted_at=None,
            deleted_by=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )
        if count:
            self.message_user(
                request, f"Restored {count} records.", level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "All selected records are already active.",
                level=messages.ERROR,
            )

    def delete_model(self, request, obj):
        """
        Custom delete method which only marks the object as deleted by setting the deleted_at and deleted_by fields,
        rather than deleting the object from the database.

        Args:
        request: The HttpRequest object.
        obj: The model object that is to be deleted.

        Returns:
        The result of the save method of the model object, which is None by default.
        """
        obj.deleted_at = timezone.now()
        obj.deleted_by = request.user
        return obj.save()

    def save_model(self, request, obj, form, change):
        """
        Override the save model function to keep track of the user who creates and updates the object.

        Args:
            request: Current HTTP request.
            obj: The model object to be saved.
            form: Form instance with the data from the request.
            change: Boolean value representing whether this is a new object or an existing one.
        """
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class DeleteActionMixin:
    """A mixin to enable the delete action on the list page and the delete button on the detail page of admin."""

    def has_delete_permission(self, request, obj=None):
        """
        Checks if delete permissions are given.

        Args:
            request: Current HTTP request.
            obj: The model object for which the permission is checked.

        Returns:
            True if permission is granted else False. Here it always returns True.
        """
        return True


class CSVActionMixin(CSVFileOrEmailModelMixin):
    """
    This Mixin adds an action to Model's Admin to download selected rows as a CSV file.
    If 'list_download' is not defined, 'list_display' will be used.
    All fields listed in 'list_skip_download' will be skipped.
    CSVActionMixin must be included before ModelAdmin, otherwise it won't work.
    The downloaded file name can be overridden by assigning a new name to `csv_file_name` class attribute.

    Attributes:
    csv_file_name: String that holds the name of the CSV file to be downloaded.
    This can be overridden in the child class.
    list_download: Tuple that holds the fields to be included in the CSV file.
    If not defined, list_display will be used.
    list_skip_download: Tuple that holds the fields to be skipped in the CSV file.
    actions: List that holds the custom actions defined for the model in the Django admin.
    """

    csv_file_name = None
    list_download = ()
    list_skip_download = ()
    actions = [
        "download_as_csv",
    ]

    # pylint: disable=protected-access,inconsistent-return-statements
    @classmethod
    def initialize_instance(cls, *args, model=None, **kwargs):
        """
        Initialize the instance by returning a model instance registered with the admin site.

        Args:
            model: Model class for which the instance should be initialized.
            *args, **kwargs: Other arguments.
        """
        for site in admin.sites.all_sites:
            try:
                return site._registry[model]
            except KeyError:
                pass

    def download_as_csv(self, request, queryset):
        """
        Downloads the selected rows in the Django admin as a CSV file.

        Args:
            request: Current HTTP request.
            queryset: The selected rows in the Django admin.

        Returns:
            A FileResponse with the CSV file or a redirection to the same page if the CSV file is too large.
        """
        try:
            buffer = self.generate_csv(request, queryset)
        except CSVTooLarge as exc:
            self.message_user(request, str(exc))
            return HttpResponseRedirect(request.get_full_path())

        compressed, buffer = self.conditional_compress(buffer)
        if compressed:
            response = FileResponse(buffer, content_type="application/gzip")
            response[
                "Content-Disposition"
            ] = f"attachment; filename={self.get_csv_file_name()}.csv.gz"
            response["Content-Length"] = file_size(buffer)
        else:
            response = HttpResponse(buffer, content_type="text/csv")
            response[
                "Content-Disposition"
            ] = f"attachment; filename={self.get_csv_file_name()}.csv"
        return response

    download_as_csv.short_description = "Download selected rows as CSV"

    def get_columns(self, request, queryset):
        """
        Get the columns for the CSV file.

        Args:
            request: Current HTTP request.
            queryset: The selected rows in the Django admin.

        Returns:
            A list of fields to be included in the CSV file.
        """
        _list_download = self.list_download or self.get_list_display(request)
        return [
            field for field in _list_download if field not in self.list_skip_download
        ]

    def get_buffer(self, queryset, columns):
        """
        Writes the queryset data to a CSV and returns the CSV as a StringIO buffer.

        Args:
        queryset: The queryset data to be written to the CSV.
        columns: The columns to be included in the CSV.

        Returns:
        The CSV data as a StringIO buffer.
        """
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, columns)
        writer.writeheader()
        for item in queryset.iterator():
            row = {}
            for field_name in columns:
                _, _, value = lookup_field(field_name, item, self)
                row[field_name] = value
            writer.writerow(row)

        buffer.seek(0, os.SEEK_SET)
        return buffer

    def get_csv_file_name(self):
        return self.csv_file_name or self.model._meta.verbose_name_plural


class ReadOnlyMixin:
    """
    This mixin disables all operations (create, update, and delete) on the model admin.

    Methods:
    has_add_permission: Returns False to disable adding (creating) new instances of the model.
    has_change_permission: Returns False to disable changing (updating) existing instances of the model.
    has_delete_permission: Returns False to disable deleting instances of the model.
    """

    def has_add_permission(self, request):
        """
        Deny adding (creating) new instances of the model.

        Args:
            request: Current HTTP request.
            obj: The model object for which the permission is checked.

        Returns:
            False, denying the permission to add.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Deny changing (updating) existing instances of the model.

        Args:
            request: Current HTTP request.
            obj: The model object for which the permission is checked.

        Returns:
            False, denying the permission to change.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Deny deleting instances of the model.

        Args:
            request: Current HTTP request.
            obj: The model object for which the permission is checked.

        Returns:
            False, denying the permission to delete.
        """
        return False
