"""
A module for lazily reading a file-like object in chunks.
"""

from typing import BinaryIO, Iterator

def iter_file_chunks(file_obj: BinaryIO, chunk_size: int) -> Iterator[bytes]:
    """
    Lazily reads a file-like object in chunks of a specified size.

    This function is a generator that yields chunks of bytes from the given
    file-like object. It reads the file piece by piece, so it is memory-efficient
    for large files. It does not read the whole file into memory at once.

    Args:
        file_obj: A file-like object opened in binary mode (e.g., the result of
                  open('file.bin', 'rb')). It must have a read() method that
                  returns bytes.
        chunk_size: The maximum size of each chunk in bytes. Must be a
                    positive integer.

    Yields:
        Non-empty chunks of bytes, where each chunk is at most chunk_size
        bytes long.

    Raises:
        ValueError: If chunk_size is not a positive integer.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    # This loop continues as long as the read() operation returns a non-empty
    # byte string. An empty byte string (b'') indicates the end of the file.
    # The walrus operator (:=) is used for a concise read-and-check loop.
    while chunk := file_obj.read(chunk_size):
        yield chunk
