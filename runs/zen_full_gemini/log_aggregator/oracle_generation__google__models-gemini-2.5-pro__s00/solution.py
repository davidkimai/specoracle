"""A module for merging and processing log streams."""

import itertools
from typing import Any, Dict, Hashable, Iterable, List, Tuple

# A type alias for a log record for improved readability.
LogRecord = Dict[str, Any]


def _get_deduplication_key(record: LogRecord) -> Tuple[Hashable, ...]:
    """Extracts the deduplication key (source, seq) from a log record.

    Args:
        record: A log record dictionary.

    Returns:
        A tuple containing the source and sequence number.

    Raises:
        ValueError: If 'source' or 'seq' keys are missing from the record.
    """
    try:
        return (record['source'], record['seq'])
    except KeyError as e:
        raise ValueError(f"Log record missing required deduplication key: {e}") from e


def _get_sort_key(record: LogRecord) -> Any:
    """Extracts the sorting key (ts) from a log record.

    Args:
        record: A log record dictionary.

    Returns:
        The value of the timestamp key 'ts'.

    Raises:
        ValueError: If the 'ts' key is missing from the record.
    """
    try:
        return record['ts']
    except KeyError as e:
        raise ValueError(f"Log record missing required sort key: {e}") from e


def _deduplicate_records(records: Iterable[LogRecord]) -> Iterable[LogRecord]:
    """Yields unique records from an iterable, based on a deduplication key.

    The first record seen for each unique key is the one that is kept.

    Args:
        records: An iterable of log records.

    Yields:
        Log records, with duplicates (by source and seq) removed.
    """
    seen_keys = set()
    for record in records:
        key = _get_deduplication_key(record)
        if key not in seen_keys:
            seen_keys.add(key)
            yield record


def merge_logs(streams: List[Iterable[LogRecord]]) -> List[LogRecord]:
    """Merges multiple log streams into a single, sorted, and deduplicated list.

    The function processes a list of log streams, where each stream is an
    iterable of log records (dictionaries). It performs the following steps:
    1. Flattens all streams into a single sequence of records.
    2. Deduplicates records based on the composite key ('source', 'seq'). The
       first occurrence of a record with a given key is kept.
    3. Sorts the resulting unique records by their timestamp ('ts').

    This function does not modify the input records.

    Args:
        streams: A list of iterables, where each iterable yields log record
                 dictionaries. Each record must contain 'source', 'seq', and
                 'ts' keys.

    Returns:
        A new list containing the merged, deduplicated, and sorted log records.

    Raises:
        TypeError: If the `streams` argument is not a list.
        ValueError: If any log record is missing one of the required keys
                    ('source', 'seq', 'ts').
    """
    if not isinstance(streams, list):
        raise TypeError(
            f"Input 'streams' must be a list of iterables, "
            f"not {type(streams).__name__}."
        )

    all_records = itertools.chain.from_iterable(streams)

    unique_records = _deduplicate_records(all_records)

    # The sorted() function consumes the iterator and creates a list in memory.
    # This is necessary because sorting requires access to the entire collection.
    sorted_records = sorted(unique_records, key=_get_sort_key)

    return sorted_records
