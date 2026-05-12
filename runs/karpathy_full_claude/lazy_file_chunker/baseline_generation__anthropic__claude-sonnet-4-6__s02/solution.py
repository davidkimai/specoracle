def iter_file_chunks(file_obj, chunk_size: int):
    """
    Lazily read from a file-like object, yielding non-empty byte chunks.

    Parameters
    ----------
    file_obj   : file-like object supporting read(size)
    chunk_size : number of bytes to read per iteration (must be > 0)

    Yields
    ------
    bytes  – successive non-empty chunks read from *file_obj*

    Raises
    ------
    ValueError  – if chunk_size is not a positive integer
    TypeError   – if chunk_size is not an integer
    """
    if not isinstance(chunk_size, int):
        raise TypeError(
            f"chunk_size must be an integer, got {type(chunk_size).__name__!r}"
        )
    if chunk_size <= 0:
        raise ValueError(
            f"chunk_size must be a positive integer, got {chunk_size!r}"
        )

    while True:
        chunk = file_obj.read(chunk_size)
        # read() returns b'' (or '') at EOF; stop iteration on empty result
        if not chunk:
            break
        yield chunk
