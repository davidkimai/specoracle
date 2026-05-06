def iter_file_chunks(file_obj, chunk_size: int, include_index: bool = False):
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
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
