"""
A module for merging and deduplicating log streams.
"""

from typing import List, Iterable, Dict, Any, Tuple

def merge_logs(streams: List[Iterable[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merges multiple log streams, deduplicates records, and sorts them by timestamp.

    Log records are dictionaries expected to contain at least 'ts', 'source',
    and 'seq' keys.

    Deduplication is based on the composite key of ('source', 'seq'). If multiple
    records share the same key, the first one encountered during iteration is kept.

    The final list of unique records is sorted by the 'ts' field in
    ascending order.

    This function does not mutate the input records.

    Args:
        streams: A list of iterables, where each iterable yields log records
                 as dictionaries.

    Returns:
        A new list of unique log records, sorted by timestamp.

    Raises:
        KeyError: If a log record is missing 'ts', 'source', or 'seq'.
    """
    unique_records: Dict[Tuple[Any, Any], Dict[str, Any]] = {}

    for stream in streams:
        for record in stream:
            # A tuple of (source, seq) serves as the unique key for a log record.
            # This will raise a KeyError if 'source' or 'seq' is missing,
            # which is the desired behavior for malformed records.
            key = (record['source'], record['seq'])

            # By checking for existence before assignment, we ensure that only the
            # first encountered record for a given key is stored.
            if key not in unique_records:
                unique_records[key] = record

    # Get the unique records from the dictionary's values.
    records_to_sort = list(unique_records.values())

    # Sort the list of unique records by the 'ts' timestamp.
    # This will raise a KeyError if 'ts' is missing from any record.
    sorted_records = sorted(records_to_sort, key=lambda r: r['ts'])

    return sorted_records
