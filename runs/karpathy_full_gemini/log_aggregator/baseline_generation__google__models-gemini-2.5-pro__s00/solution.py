import collections.abc
import typing

# A type alias for a log record dictionary for improved readability and type checking.
LogRecord = typing.Dict[str, typing.Any]


def merge_logs(streams: list[collections.abc.Iterable[LogRecord]]) -> list[LogRecord]:
    """
    Merges multiple log streams, deduplicates records, and sorts them by timestamp.

    This function processes a list of iterables, where each iterable yields log
    records as dictionaries. It combines all records into a single collection,
    ensuring that each record, identified by a composite key of its 'source'
    and 'seq' values, is unique. The first occurrence of a record with a
    given (source, seq) key is retained.

    The resulting list of unique records is then sorted in ascending order based
    on the 'ts' (timestamp) value of each record. The original input records
    are not modified.

    Args:
        streams: A list of iterables, each yielding log record dictionaries.
                 Each dictionary is expected to contain 'ts', 'source', and 'seq'
                 keys. The values for 'source' and 'seq' must be hashable, and
                 the values for 'ts' must be comparable.

    Returns:
        A new list containing the unique log records, sorted by timestamp.

    Raises:
        ValueError: If a log record is missing a required key ('ts', 'source', 'seq').
        TypeError: If 'ts' values are not comparable (e.g., mixed types), or if
                   'source' or 'seq' values are not hashable.
    """
    # Use a dictionary to store unique records, with (source, seq) as the key.
    # This efficiently handles deduplication, keeping the first-seen record.
    unique_records: typing.Dict[typing.Tuple[typing.Any, typing.Any], LogRecord] = {}

    for stream in streams:
        for record in stream:
            try:
                # Create a composite key for deduplication.
                key = (record['source'], record['seq'])
            except KeyError as e:
                raise ValueError(
                    f"Record missing required key for deduplication ('source' or 'seq'): {e}"
                ) from e
            except TypeError:
                # This occurs if 'source' or 'seq' values are unhashable (e.g., a list).
                raise TypeError(
                    f"Unhashable type for 'source' or 'seq' in record: {record}"
                )

            if key not in unique_records:
                unique_records[key] = record

    # Extract the unique records from the dictionary.
    deduplicated_list = list(unique_records.values())

    # Sort the final list of records by the 'ts' key.
    try:
        # The sorted() function returns a new sorted list.
        return sorted(deduplicated_list, key=lambda r: r['ts'])
    except KeyError as e:
        raise ValueError(
            f"Record missing 'ts' key required for sorting: {e}"
        ) from e
    except TypeError:
        # This occurs if 'ts' values are of mixed, non-comparable types.
        raise TypeError("Inconsistent or non-comparable 'ts' types found in records.")
