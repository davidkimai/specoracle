# -*- coding: utf-8 -*-
"""
A module for merging and deduplicating log streams.
"""

from typing import Any, Dict, Iterable, List, Tuple

# A type alias for a log record, which is a dictionary.
LogRecord = Dict[str, Any]


def merge_logs(streams: List[Iterable[LogRecord]]) -> List[LogRecord]:
    """
    Merges multiple log streams, deduplicates records, and sorts them by timestamp.

    This function processes a list of log streams, where each stream is an
    iterable of log records (dictionaries). It combines all records into a
    single list, ensuring that each record is unique based on a composite
    key of its 'source' and 'seq' values. If duplicates are found, only the
    first one encountered is kept.

    The final list of unique records is then sorted in ascending order based on
    the 'ts' (timestamp) key.

    The function operates without modifying the original log records provided
    in the input streams.

    Args:
        streams: A list of iterables. Each iterable yields log records.
                 A log record is a dictionary that must contain 'ts',
                 'source', and 'seq' keys.

    Returns:
        A new list containing the unique, sorted log records.

    Raises:
        KeyError: If a log record is missing the 'ts', 'source', or 'seq' key.
        TypeError: If 'source' or 'seq' values are not hashable, or if 'ts'
                   values from different records are not comparable.
    """
    unique_records: Dict[Tuple[Any, Any], LogRecord] = {}

    for stream in streams:
        for record in stream:
            # Create a composite key for deduplication.
            # This will raise a KeyError if 'source' or 'seq' is missing.
            key = (record["source"], record["seq"])

            # Use the dictionary to ensure uniqueness. The first record
            # encountered for a given key is stored. Subsequent records
            # with the same key are ignored.
            if key not in unique_records:
                unique_records[key] = record

    # Extract the unique log records from the dictionary's values.
    # The order of values is not guaranteed, but that is resolved by sorting.
    deduplicated_records = list(unique_records.values())

    # Sort the list of records by the 'ts' key.
    # The sorted() function creates and returns a new sorted list.
    # This will raise a KeyError if 'ts' is missing or a TypeError
    # if timestamps are not comparable.
    return sorted(deduplicated_records, key=lambda r: r["ts"])
