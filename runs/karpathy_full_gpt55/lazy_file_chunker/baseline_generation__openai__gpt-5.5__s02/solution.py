from collections.abc import Iterator
from typing import Protocol


class _ReadableBytes(Protocol):
    def read(self, size: int = -1) -> bytes:
        ...


def iter_file_chunks(file_obj: _ReadableBytes, chunk_size: int) -> Iterator[bytes]:
    """
    Lazily read non-empty byte chunks from a binary file-like object.

    Args:
        file_obj: An object providing read(size) and returning bytes.
        chunk_size: The maximum number of bytes to request per read.

    Yields:
        Non-empty bytes objects until EOF.

    Raises:
        TypeError: If chunk_size is not an integer, or if read() returns non-bytes.
        ValueError: If chunk_size is not positive.
    """
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    while True:
        chunk = file_obj.read(chunk_size)

        if chunk == b"":
            break

        if not isinstance(chunk, bytes):
            raise TypeError("file_obj.read() must return bytes")

        yield chunk


__all__ = ["iter_file_chunks"]
