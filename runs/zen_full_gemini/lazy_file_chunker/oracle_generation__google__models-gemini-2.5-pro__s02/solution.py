# -*- coding: utf-8 -*-
"""
A module for lazily reading a file-like object in fixed-size chunks.
"""

import typing

__all__ = ["iter_file_chunks"]


def iter_file_chunks(
    file_obj: typing.IO[bytes], chunk_size: int
) -> typing.Iterator[bytes]:
    """
    Lazily reads a file-like object, yielding non-empty byte chunks.

    This function reads from the file-like object's current position and
    yields chunks until the end of the file is reached. It is designed to
    handle large files efficiently by not loading the entire content into
    memory at once.

    Args:
        file_obj: A file-like object opened in binary mode. It must have a
                  `read(size)` method that returns bytes.
        chunk_size: The maximum size of each chunk in bytes.

    Yields:
        Non-empty chunks of bytes from the file. The last chunk may be
        smaller than `chunk_size`.

    Raises:
        TypeError: If `chunk_size` is not an integer.
        ValueError: If `chunk_size` is not a positive integer.
    """
    _validate_chunk_size(chunk_size)

    # The loop continues as long as the read operation returns a non-empty
    # byte string. The walrus operator (:=) assigns the result of read()
    # to `chunk` and then the `while` statement checks its truthiness.
    # An empty byte string (b'') evaluates to False, terminating the loop.
    while chunk := file_obj.read(chunk_size):
        yield chunk


def _validate_chunk_size(chunk_size: int) -> None:
    """
    Ensures that the chunk size is a positive integer.
    
    This helper centralizes input validation for the chunk size parameter,
    making the main function's logic cleaner.
    """
    if not isinstance(chunk_size, int):
        raise TypeError(
            f"chunk_size must be an integer, not {type(chunk_size).__name__}."
        )

    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
