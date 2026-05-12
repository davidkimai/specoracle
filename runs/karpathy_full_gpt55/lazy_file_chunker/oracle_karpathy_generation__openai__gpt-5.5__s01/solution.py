from collections.abc import Iterator


def iter_file_chunks(file_obj, chunk_size: int) -> Iterator[bytes]:
    """Yield non-empty bytes chunks read lazily from file_obj."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    while True:
        chunk = file_obj.read(chunk_size)
        if not isinstance(chunk, bytes):
            raise TypeError("file_obj.read() must return bytes")
        if not chunk:
            break
        yield chunk
