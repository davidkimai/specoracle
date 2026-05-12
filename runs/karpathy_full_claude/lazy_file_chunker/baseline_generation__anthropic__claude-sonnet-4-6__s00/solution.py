def iter_file_chunks(file_obj, chunk_size: int):
    """
    Lazily read from a file-like object, yielding non-empty byte chunks.

    Parameters
    ----------
    file_obj  : a file-like object that supports read(size)
    chunk_size: number of bytes to read per iteration; must be positive

    Yields
    ------
    bytes chunks (non-empty)

    Raises
    ------
    ValueError if chunk_size is not positive
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError(
            f"chunk_size must be a positive integer, got {chunk_size!r}"
        )

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
