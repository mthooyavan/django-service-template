import gzip
import io
import os
from contextlib import contextmanager

from django.conf import settings


@contextmanager
def safe_reading(file):
    """
    Context manager for safely reading a file without altering the current file position.

    This context manager saves the current position of the file before setting the file position to the start.
    After the block of code inside the 'with' statement finishes, the file's position is reset to the original location.

    Parameters:
    file (file-like object): The file to be read

    Yields:
    None: This function yields control back to the context.
    """
    old_file_position = file.tell()
    file.seek(0, os.SEEK_END)
    yield
    file.seek(old_file_position, os.SEEK_SET)


def file_size(file) -> int:
    """
    Calculate the size of a file.

    This function returns the size of the file in bytes. If the file object has a '_size' attribute,
    that value is returned. Otherwise, the function calculates the size by reading the whole file and
    returning the position of the end of the file.

    Parameters:
    file (file-like object): The file for which to calculate the size

    Returns:
    int: The size of the file in bytes
    """
    size = getattr(file, "_size", None)
    if size is not None:
        return size

    with safe_reading(file):
        return file.tell()


class CSVFileCompressionMixin:
    """
    This class provides methods to compress a csv file using gzip.
    """

    def compress(self, file, encoding="utf-8"):
        """
        Compress a file using gzip.

        This method reads lines from the input file, encodes them using the specified encoding,
        and writes the encoded data to a gzipped BytesIO buffer.

        Parameters:
        file (file-like object): The file to compress
        encoding (str): The encoding to use when reading the file

        Returns:
        io.BytesIO: A BytesIO object containing the gzipped file
        """
        buffer = io.BytesIO()
        with gzip.GzipFile(mode="w", fileobj=buffer) as z_file:
            for line in file:
                z_file.write(line.encode(encoding))
        buffer.seek(0, os.SEEK_SET)
        return buffer

    def conditional_compress(self, file, force=False):
        """
        Conditionally compress a file.

        This method checks whether the file should be compressed. If the file should be compressed or
        if the 'force' parameter is True, the file is compressed. Otherwise, the original file is returned.

        Parameters:
        file (file-like object): The file to potentially compress
        force (bool): If True, the file is compressed regardless of its size

        Returns:
        tuple: A tuple where the first element is a boolean indicating whether the file was compressed,
               and the second element is either the original file or the compressed file
        """
        if force or should_compress(file):
            compressed = True
            new_file = self.compress(file)
        else:
            compressed = False
            new_file = file
        return compressed, new_file


def should_compress(file) -> bool:
    """
    Determine whether a file should be compressed.

    This function checks whether the size of the file is greater than or equal to
    the threshold specified in the settings.

    Parameters:
    file (file-like object): The file to check

    Returns:
    bool: True if the file should be compressed, False otherwise
    """
    return file_size(file) >= settings.ENFORCE_COMPRESSION_FILE_SIZE
