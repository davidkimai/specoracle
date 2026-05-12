from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol


class _Readable(Protocol):
    def read(self, size: int = -1) -> bytes:
        ...


def iter_file_chunks(file_obj: _Readable, chunk_size: int) -> Iterator[bytes]:
    """
    Lazily yield non-empty byte chunks read from a file-like object.

    Args:
        file_obj: An object providing read(size) that returns bytes.
        chunk_size: The maximum number of bytes to request per read.

    Raises:
        ValueError: If chunk_size is not positive.
        AttributeError: If file_obj has no read attribute.
        TypeError: If read(size) returns a non-bytes object.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    read = file_obj.read

    def _iterator() -> Iterator[bytes]:
        while True:
            chunk = read(chunk_size)
            if chunk == b"":
                break
            if not isinstance(chunk, bytes):
                raise TypeError("file_obj.read(size) must return bytes")
            yield chunk

    return _iterator()
