"""
lazy_file_chunker
~~~~~~~~~~~~~~~~~
Lazily read a file-like object in fixed-size byte chunks.
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
    bytes
        Each chunk read from the file when *include_index* is ``False``.
    tuple[int, bytes]
        ``(index, chunk)`` pairs when *include_index* is ``True``.
        The final chunk may be smaller than *chunk_size*.  Empty reads
        (EOF) stop iteration.

    Raises
    ------
    ValueError
        If *chunk_size* is not a positive integer.
    """
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool):
        raise ValueError(f"chunk_size must be an int, got {type(chunk_size).__name__!r}")
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size!r}")

    index = 0
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            return
        if include_index:
            yield (index, chunk)
        else:
            yield chunk
        index += 1
