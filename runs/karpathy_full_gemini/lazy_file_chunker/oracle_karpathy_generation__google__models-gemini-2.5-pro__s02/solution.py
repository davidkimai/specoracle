# lazy_file_chunker.py

"""
A module for lazily reading a file-like object in chunks.
"""

import typing

def iter_file_chunks(
    file_obj: typing.IO[bytes],
    chunk_size: int
) -> typing.Iterator[bytes]:
    """
    Lazily reads a file-like object and yields its contents in chunks.

    This function reads from the file object in chunks of the specified size
    without loading the entire file into memory. It is suitable for processing
    large files.

    Args:
        file_obj: A file-like object opened in binary mode. It must have a
                  `read(size)` method that returns bytes.
        chunk_size: The size of each chunk in bytes. Must be a positive integer.

    Yields:
        Bytes chunks of size at most `chunk_size`. The last chunk may be smaller.
        Only non-empty chunks are yielded.

    Raises:
        ValueError: If `chunk_size` is not a positive integer.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
