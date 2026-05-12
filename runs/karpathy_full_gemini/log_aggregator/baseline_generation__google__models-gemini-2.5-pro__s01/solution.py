"""
A module for merging and sorting log streams.

This module provides a function to aggregate multiple log streams into a single,
sorted, and deduplicated list of log records.
"""

from typing import Iterable, List, Dict, Any, Tuple

# A type alias for a log record dictionary for improved readability.
LogRecord = Dict[str, Any]


def merge_logs(streams: List[Iterable[LogRecord]]) -> List[LogRecord]:
    """
    Merges multiple log streams, deduplicates records, and sorts them by timestamp.

    This function takes a list of log streams, where each stream is an
    iterable of log records (dictionaries). It combines all records from all
    streams, ensuring that only the first record encountered for each unique
    (source, seq) pair is retained. The final list of unique records is then
    sorted by the timestamp ('ts') in ascending order.

    The original input log records are not mutated.

    Args:
        streams: A list of iterables, where each iterable yields log
                 records. A log record is a dictionary expected to
                 contain at least 'ts', 'source', and 'seq' keys.

    Returns:
        A new list containing the merged, deduplicated, and sorted
        log records.

    Raises:
        ValueError: If a log record is missing one of the required keys
                    ('ts', 'source', 'seq').
    """
    unique_records: Dict[Tuple[Any, Any], LogRecord] = {}

    for stream in streams:
        for record in stream:
            try:
                # Create a unique key for each log record based on its
                # source and sequence number. This assumes 'source' and 'seq'
                # values are hashable.
                key = (record['source'], record['seq'])
            except KeyError as e:
                raise ValueError(
                    f"Log record missing required key for deduplication: {e}"
                ) from e

            # Add the record to our dictionary if its key has not been seen.
            # This handles deduplication by keeping the first record
            # encountered for any given (source, seq) pair.
            if key not in unique_records:
                unique_records[key] = record

    # Extract the unique records from the dictionary's values.
    deduplicated_records = list(unique_records.values())

    try:
        # Sort the list of unique records by their timestamp ('ts').
        # A lambda function is used to specify the sort key. This assumes
        # the 'ts' value is present and comparable.
        sorted_records = sorted(deduplicated_records, key=lambda r: r['ts'])
    except KeyError as e:
        raise ValueError(
            f"Log record missing required key for sorting: {e}"
        ) from e

    return sorted_records
