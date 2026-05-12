"""A module for lazily reading a file-like object in chunks."""

from typing import IO, Iterator

__all__ = ["iter_file_chunks"]


def iter_file_chunks(file_obj: IO[bytes], chunk_size: int) -> Iterator[bytes]:
    """
    Lazily reads a file-like object, yielding non-empty chunks of bytes.

    This function reads from the file object in chunks of the specified size
    until the end of the file is reached. It is memory-efficient as it does
    not load the entire file into memory at once.

    Args:
        file_obj: A file-like object opened in binary mode with a read() method.
        chunk_size: The maximum size of each chunk in bytes.

    Yields:
        Non-empty byte chunks read from the file.

    Raises:
        ValueError: If chunk_size is not a positive integer.
        TypeError: If chunk_size is not an integer.
    """
    if not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    while chunk := file_obj.read(chunk_size):
        yield chunk
