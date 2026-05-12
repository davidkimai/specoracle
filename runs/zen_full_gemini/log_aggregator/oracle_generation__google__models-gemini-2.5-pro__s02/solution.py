"""
A module for merging and sorting log streams.
"""

from typing import Any, Dict, Generator, Iterable, List, Tuple


def _flatten_and_validate_records(
    streams: List[Iterable[Dict[str, Any]]]
) -> Generator[Tuple[int, int, Dict[str, Any]], None, None]:
    """
    Flattens a list of log streams and validates each record's structure.

    This helper function iterates through each stream and each record, ensuring
    the inputs are of the correct type and that each log record dictionary
    contains the required keys.

    Args:
        streams: A list of iterables, where each iterable yields log records.

    Yields:
        A tuple containing the stream index, record index, and the valid log
        record from the input streams.

    Raises:
        TypeError: If `streams` is not a list, an element in `streams` is not
                   an iterable, or a log record is not a dictionary.
        ValueError: If a log record is missing a required key.
    """
    if not isinstance(streams, list):
        raise TypeError("Input 'streams' must be a list of iterables.")

    for i, stream in enumerate(streams):
        if not hasattr(stream, '__iter__'):
            raise TypeError(f"Item at index {i} in 'streams' is not an iterable.")

        for j, record in enumerate(stream):
            if not isinstance(record, dict):
                error_msg = (
                    f"Log record at stream {i}, index {j} must be a dict, "
                    f"but got {type(record).__name__}."
                )
                raise TypeError(error_msg)

            required_keys = ['source', 'seq', 'ts']
            for key in required_keys:
                if key not in record:
                    error_msg = (
                        f"Log record at stream {i}, index {j} is missing "
                        f"required key: '{key}'."
                    )
                    raise ValueError(error_msg)

            yield i, j, record


def merge_logs(
    streams: List
