from typing import Iterator


def iter_file_chunks(file_obj, chunk_size: int) -> Iterator[bytes]:
    """Yield non-empty byte chunks from a file-like object until EOF."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
