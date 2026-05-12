"""
A module for lazily reading a file-like object in fixed-size chunks.
"""

from typing import IO, Iterator


def iter_file_chunks(file_obj: IO[bytes], chunk_size: int) -> Iterator[bytes]:
    """
    Lazily reads a file-like object in chunks of a specified size.

    This function reads from the file object's current position and continues
    until the end of the file is reached. It yields non-empty byte chunks.

    Args:
        file_obj: A file-like object opened in binary mode, with a `read()` method.
        chunk_size: The maximum size of each chunk in bytes. Must be positive.

    Yields:
        A `bytes` object representing a chunk of the file. The last chunk may be
        smaller than `chunk_size`.

    Raises:
        ValueError: If `chunk_size` is not a positive integer.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            # An empty bytes object signifies the end of the file.
            break
        yield chunk
