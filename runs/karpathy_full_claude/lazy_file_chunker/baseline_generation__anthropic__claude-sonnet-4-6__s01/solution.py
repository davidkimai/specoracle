def iter_file_chunks(file_obj, chunk_size: int):
    """
    Iterate over a file-like object, yielding non-empty byte chunks of the given size.

    :param file_obj: A file-like object supporting read(size).
    :param chunk_size: The number of bytes to read per chunk. Must be positive.
    :raises ValueError: If chunk_size is not positive.
    :yields: Non-empty bytes chunks read from file_obj.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError(f"chunk_size must be a positive integer, got {chunk_size!r}")

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
