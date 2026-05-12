"""
A module for lazily reading a file-like object in fixed-size chunks.

This module provides a generator function to iterate over a binary file-like
object, yielding its content in non-empty chunks of a specified size.
"""

import typing

__all__ = ["iter_file_chunks"]


def iter_file_chunks(
    file_obj: typing.IO[bytes], chunk_size: int
) -> typing.Iterator[bytes]:
    """
    Lazily reads a file-like object in chunks of a specified size.

    This function reads from the file object chunk by chunk, yielding each
    non-empty chunk of bytes. It does not read the entire file into memory at once.
    The caller is responsible for managing the lifecycle (opening and closing) of
    the file object.

    Args:
        file_obj: A file-like object opened in binary mode, providing a read()
                  method that returns bytes.
        chunk_size: The maximum size of each chunk in bytes. Must be a positive
                    integer.

    Yields:
        Non-empty chunks of bytes read from the file.

    Raises:
        ValueError: If chunk_size is not a positive integer.
        TypeError: If chunk_size is not an integer.
    """
    if not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer.")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            # An empty byte string (b'') signifies the end of the file.
            break
        yield chunk
