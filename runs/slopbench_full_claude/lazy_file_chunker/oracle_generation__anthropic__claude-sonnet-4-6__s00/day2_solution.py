"""
lazy_file_chunker - yield fixed-size byte chunks from a file-like object.
"""


def iter_file_chunks(file_obj, chunk_size: int, include_index: bool = False):
    """Yield non-empty byte chunks of *chunk_size* from *file_obj*.

    Parameters
    ----------
    file_obj:
        Any object that implements ``read(size) -> bytes``.
    chunk_size:
        Number of bytes to request per read.  Must be a positive integer.
    include_index:
        When ``True``, yield ``(index, chunk)`` tuples where *index* is the
        zero-based chunk number.  When ``False`` (default), yield bare
        ``bytes`` chunks.

    Yields
    ------
    bytes or tuple[int, bytes]
        Successive chunks; the final chunk may be shorter than *chunk_size*.
        If *include_index* is ``True``, each item is ``(index, chunk)``.

    Raises
    ------
    ValueError
        If *chunk_size* is not a positive integer.
    """
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool):
        raise ValueError(f"chunk_size must be an integer, got {type(chunk_size).__name__!r}")
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size!r}")

    index = 0
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        if include_index:
            yield (index, chunk)
        else:
            yield chunk
        index += 1
