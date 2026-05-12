from collections.abc import Callable, Iterator
from typing import Any


def iter_file_chunks(file_obj: Any, chunk_size: int) -> Iterator[bytes]:
    """Return an iterator over non-empty byte chunks read lazily from file_obj."""
    size = _validate_chunk_size(chunk_size)
    read = _get_read_method(file_obj)
    return _read_chunks(read, size)


def _validate_chunk_size(chunk_size: int) -> int:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return chunk_size


def _get_read_method(file_obj: Any) -> Callable[[int], bytes]:
    read = getattr(file_obj, "read", None)
    if not callable(read):
        raise TypeError("file_obj must provide a callable read(size) method")
    return read


def _read_chunks(read: Callable[[int], bytes], chunk_size: int) -> Iterator[bytes]:
    while True:
        chunk = read(chunk_size)
        if not isinstance(chunk, bytes):
            raise TypeError("file_obj.read(size) must return bytes")
        if chunk == b"":
            return
        yield chunk
