def iter_file_chunks(file_obj, chunk_size: int):
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
