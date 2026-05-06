"""
lazy_file_chunker
~~~~~~~~~~~~~~~~~
Lazily read a file-like object in fixed-size byte chunks.
"""


def iter_file_chunks(file_obj, chunk_size: int):
    """Yield non-empty byte chunks of *chunk_size* from *file_obj*.

    Parameters
    ----------
    file_obj:
        Any object that implements ``read(size) -> bytes``.
    chunk_size:
        Number of bytes to request per read.  Must be a positive integer.

    Yields
    ------
    bytes
        Each chunk read from the file.  The final chunk may be smaller than
        *chunk_size*.  Empty reads (EOF) stop iteration.

    Raises
    ------
    ValueError
        If *chunk_size* is not a positive integer.
    """
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool):
        raise ValueError(f"chunk_size must be an int, got {type(chunk_size).__name__!r}")
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size!r}")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            return
        yield chunk
