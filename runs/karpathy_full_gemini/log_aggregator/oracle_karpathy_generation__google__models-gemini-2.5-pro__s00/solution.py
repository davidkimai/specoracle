"""
A module for merging and deduplicating log streams.
"""

from typing import Any, Dict, Iterable, List, Tuple


def merge_logs(streams: List[Iterable[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merges multiple log streams, deduplicates records by (source, seq),
    and returns records sorted by timestamp.

    The deduplication strategy keeps the first record encountered for any
    given (source, seq) pair. Input records are not mutated.

    Args:
        streams: A list of iterables, where each iterable yields log records.
                 Each log record is a dictionary expected to have at least
                 'ts' (timestamp), 'source', and 'seq' (sequence number) keys.

    Returns:
        A single list of unique log records, sorted by the 'ts' key in
        ascending order.
    """
    unique_records: Dict[Tuple[Any, Any], Dict[str, Any]] = {}

    for stream in streams:
        for record in stream:
            # Create a unique key for each log record based on its source and
            # sequence number. This assumes 'source' and 'seq' are present
            # and their values are hashable.
            try:
                key = (record['source'], record['seq'])
            except KeyError:
                # Assuming records that lack 'source' or 'seq' should be
                # ignored as they cannot be deduplicated according to the rule.
                # A more complex error handling strategy could be implemented
                # if needed.
                continue

            # If we haven't seen this (source, seq) pair before, add the
            # record to our collection of unique records. This ensures that
            # we keep the first occurrence of any duplicate records.
            if key not in unique_records:
                unique_records[key] = record

    # Extract the unique records from the dictionary.
    deduplicated_logs = list(unique_records.values())

    # Sort the deduplicated records by their timestamp.
    # This assumes the 'ts' value is present and comparable.
    # A KeyError will be raised if a record is missing 'ts'.
    sorted_logs = sorted(deduplicated_logs, key=lambda r: r['ts'])

    return sorted_logs
