from collections.abc import Iterator
from typing import Any


def iter_file_chunks(file_obj: Any, chunk_size: int) -> Iterator[bytes]:
    """
    Lazily read non-empty byte chunks from a binary file-like object.

    Args:
        file_obj: An object providing a callable read(size) method.
        chunk_size: The maximum number of bytes to request per read.

    Returns:
        An iterator yielding non-empty bytes objects.

    Raises:
        TypeError: If chunk_size is not an integer, file_obj does not provide a
            callable read method, or read() returns a non-bytes-like value.
        ValueError: If chunk_size is not positive.
    """
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool):
        raise TypeError("chunk_size must be a positive integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    read = getattr(file_obj, "read", None)
    if not callable(read):
        raise TypeError("file_obj must provide a callable read(size) method")

    def _chunks() -> Iterator[bytes]:
        while True:
            data = read(chunk_size)

            if isinstance(data, bytes):
                if not data:
                    break
                yield data
            elif isinstance(data, bytearray):
                if not data:
                    break
                yield bytes(data)
            elif isinstance(data, memoryview):
                if len(data) == 0:
                    break
                yield data.tobytes()
            else:
                raise TypeError("file_obj.read(size) must return a bytes-like object")

    return _chunks()
