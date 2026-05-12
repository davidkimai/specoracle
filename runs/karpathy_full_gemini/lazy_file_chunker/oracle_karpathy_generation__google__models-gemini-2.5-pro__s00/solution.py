"""
A module for lazily reading a file in chunks.
"""

from typing import BinaryIO, Iterator

def iter_file_chunks(file_obj: BinaryIO, chunk_size: int) -> Iterator[bytes]:
    """
    Lazily reads a file-like object in chunks.

    This function reads from the given binary file-like object `file_obj`
    in chunks of `chunk_size` bytes and yields each chunk. It does not
    load the entire file into memory, making it suitable for large files.

    Args:
        file_obj: A file-like object opened in binary mode with a read(size)
                  method.
        chunk_size: The maximum size of each chunk in bytes. Must be a
                    positive integer.

    Yields:
        Non-empty byte chunks from the file.

    Raises:
        ValueError: If chunk_size is not a positive integer.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            # End of file is reached when read() returns an empty bytes object.
            break
        yield chunk
