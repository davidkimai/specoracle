"""
A module for lazily reading a file-like object in chunks.
"""

import typing

def iter_file_chunks(
    file_obj: typing.BinaryIO, chunk_size: int
) -> typing.Iterator[bytes]:
    """
    Lazily reads a file-like object and yields its contents in chunks.

    This function reads from the file object in chunks of the specified size
    until the end of the file is reached. It is memory-efficient as it does
    not load the entire file into memory at once.

    Args:
        file_obj: A file-like object opened in binary mode. It must have a
                  `read(size)` method that returns bytes.
        chunk_size: The maximum size of each chunk in bytes. Must be a
                    positive integer.

    Yields:
        Non-empty byte chunks from the file. The last chunk may be smaller
        than chunk_size.

    Raises:
        ValueError: If chunk_size is not a positive integer.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            # End of file is reached when read() returns an empty byte string.
            break
        yield chunk
