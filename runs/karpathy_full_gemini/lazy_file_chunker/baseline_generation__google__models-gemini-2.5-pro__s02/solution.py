"""
A module for lazily reading a file-like object in chunks.
"""

import typing

__all__ = ["iter_file_chunks"]


def iter_file_chunks(
    file_obj: typing.BinaryIO, chunk_size: int
) -> typing.Iterator[bytes]:
    """
    Lazily reads a file-like object and yields its content in chunks.

    This function reads from the given binary file-like object in chunks of
    a specified size. It is a generator and does not load the entire file
    into memory. The caller is responsible for opening and closing the
    file object.

    Args:
        file_obj: A file-like object opened in binary mode with a `read()` method.
        chunk_size: The maximum size of each chunk in bytes. Must be a
                    positive integer.

    Yields:
        Non-empty byte chunks from the file.

    Raises:
        ValueError: If chunk_size is not a positive integer.
        IOError: If there is an error reading from the file object.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            # End of file is indicated by an empty byte string.
            break
        yield chunk
