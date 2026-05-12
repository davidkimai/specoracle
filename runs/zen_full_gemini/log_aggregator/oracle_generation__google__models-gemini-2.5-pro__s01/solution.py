"""
A module for merging and sorting log records from multiple streams.
"""

import collections.abc
import typing

# Type aliases for improving readability and maintainability.
LogRecord = typing.Dict[str, typing.Any]
LogStream = typing.Iterable[LogRecord]
DeduplicationKey = typing.Tuple[typing.Any, typing.Any]


def _validate_record(record: LogRecord) -> None:
    """
    Checks if a log record is a dictionary containing the required keys.

    Args:
        record: The log record to validate.

    Raises:
        TypeError: If the record is not a dictionary.
        ValueError: If the record is missing one or more required keys.
    """
    if not isinstance(record, dict):
        raise TypeError(
            f"Log record must be a dict, but got {type(record).__name__}."
        )

    required_keys = {'ts', 'source', 'seq'}
    missing_keys = required_keys.difference(record.keys())

    if missing_keys:
        # Sort for a deterministic and readable error message.
        raise ValueError(
            f"Log record is missing required keys: {sorted(list(missing_keys))}."
        )


def _get_deduplication_key(record: LogRecord) -> DeduplicationKey:
    """
    Extracts the deduplication key (source, seq) from a log record.

    This function assumes the record has already been validated to contain
    the necessary keys.

    Args:
        record: The log record.

    Returns:
        A tuple containing the source and sequence number for deduplication.
    """
    return (record['source'], record['seq'])


def merge_logs(streams: typing.List[LogStream]) -> typing.List[LogRecord]:
    """
    Merges log records from multiple streams, deduplicates, and sorts them.

    This function aggregates records from all provided streams, ensures uniqueness
    based on a composite key of ('source', 'seq'), and then returns the
    consolidated records sorted by their 'ts' timestamp. The first-encountered
    record for any given ('source', 'seq') pair is the one that is kept.

    The function does not mutate the input records.

    Args:
        streams: A list of iterables. Each iterable should yield log records,
                 which are dictionaries expected to have 'ts', 'source', and
                 'seq' keys.

    Returns:
        A single list of unique log records, sorted by timestamp.

    Raises:
        TypeError: If the 'streams' argument is not a list, if any element
                   in 'streams' is not an iterable, or if any record is not a
                   dictionary.
        ValueError: If a log record is missing required keys ('ts', 'source',
                    'seq').
    """
    if not isinstance(streams, list):
        raise TypeError(
            f"Input must be a list of streams, but got {type(streams).__name__}."
        )

    unique_records: typing.Dict[DeduplicationKey, LogRecord] = {}

    for i, stream in enumerate(streams):
        if not isinstance(stream, collections.abc.Iterable):
            raise TypeError(
                f"Item at index {i} in 'streams' list must be an iterable."
            )

        for record in stream:
            _validate_record(record)
            key = _get_deduplication_key(record)

            if key not in unique_records:
                # Store the first occurrence of a record with this key.
                unique_records[key] = record

    # Extract the unique records from the dictionary's values.
    deduplicated_records = list(unique_records.values())

    # Sort the collected records by their timestamp.
    # The 'ts' value is assumed to be a comparable type.
    sorted_records = sorted(
        deduplicated_records,
        key=lambda r: r['ts']
    )

    return sorted_records
