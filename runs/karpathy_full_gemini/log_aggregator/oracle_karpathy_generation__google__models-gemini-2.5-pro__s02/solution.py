"""
A module for merging and sorting log streams.
"""

from typing import Any, Dict, Iterable, List, Tuple


def merge_logs(streams: List[Iterable[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merges multiple log streams, deduplicates records, and sorts by timestamp.

    This function aggregates records from multiple streams. Duplicates are
    identified by a composite key of ('source', 'seq'). For any set of
    duplicate records, the last one encountered in the input streams is kept.
    The final list of unique records is sorted in ascending order by the 'ts'
    (timestamp) value.

    This function does not mutate the input records.

    Args:
        streams: A list of iterables, where each iterable yields log records.
                 A log record is a dictionary expected to contain at least
                 'ts', 'source', and 'seq' keys.

    Returns:
        A new list containing the unique, sorted log records.

    Raises:
        KeyError: If a log record is missing one of the required keys
                  ('ts', 'source', 'seq').
        TypeError: If a value for 'source' or 'seq' is not hashable.
    """
    unique_records: Dict[Tuple[Any, Any], Dict[str, Any]] = {}

    for stream in streams:
        for record in stream:
            # The composite key for deduplication is the tuple (source, seq).
            # This requires 'source' and 'seq' to be hashable types.
            key = (record['source'], record['seq'])
            unique_records[key] = record

    # Extract the collection of unique log records from the dictionary.
    # The order of values is not guaranteed at this stage.
    deduplicated_records = list(unique_records.values())

    # Sort the records based on the timestamp 'ts'.
    # This requires the 'ts' value to be a comparable type (e.g., int, float).
    sorted_records = sorted(deduplicated_records, key=lambda r: r['ts'])

    return sorted_records
