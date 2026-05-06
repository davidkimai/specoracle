def iter_file_chunks(file_obj, chunk_size: int, include_index: bool = False):
    """
    Lazily read from a file-like object, yielding non-empty byte chunks
    of at most chunk_size bytes.

    Parameters
    ----------
    file_obj      : a file-like object that supports read(size)
    chunk_size    : number of bytes to request per read call (must be > 0)
    include_index : if True, yield (index, chunk) tuples instead of bare chunks

    Yields
    ------
    bytes chunks read from file_obj, or (int, bytes) tuples when include_index is True
    """
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool):
        raise TypeError("chunk_size must be an integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

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
