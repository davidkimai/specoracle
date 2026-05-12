from collections.abc import Callable, Iterator
from typing import Any

__all__ = ["iter_file_chunks"]


def _validate_chunk_size(chunk_size: int) -> None:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")


def _get_read_method(file_obj: Any) -> Callable[[int], bytes]:
    read = getattr(file_obj, "read", None)
    if not callable(read):
        raise TypeError("file_obj must provide a callable read(size) method")
    return read


def _chunk_iterator(read: Callable[[int], bytes], chunk_size: int) -> Iterator[bytes]:
    while True:
        chunk = read(chunk_size)
        if chunk == b"":
            break
        if not isinstance(chunk, bytes):
            raise TypeError("file_obj.read(size) must return bytes")
        yield chunk


def iter_file_chunks(file_obj: Any, chunk_size: int) -> Iterator[bytes]:
    _validate_chunk_size(chunk_size)
    read = _get_read_method(file_obj)
    return _chunk_iterator(read, chunk_size)
