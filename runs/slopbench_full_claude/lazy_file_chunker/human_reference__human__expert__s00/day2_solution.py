from __future__ import annotations

from collections.abc import Iterator
from typing import BinaryIO, Union


def iter_file_chunks(
    file_obj: BinaryIO,
    chunk_size: int,
    include_index: bool = False,
) -> Iterator[Union[bytes, tuple[int, bytes]]]:
    if chunk_size <= 0:
        raise ValueError('chunk_size must be positive')
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
