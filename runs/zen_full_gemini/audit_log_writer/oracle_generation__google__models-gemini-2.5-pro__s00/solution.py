"""
A module for writing audit log records with monotonic sequence numbers.
"""

import threading
from typing import Any, Dict, List


class AuditLogWriter:
    """
    Writes audit log records to a sink with monotonic sequence numbers.

    This class ensures that each record has a unique, strictly increasing
    sequence number. The writer is thread-safe, allowing multiple threads to
    write records concurrently without race conditions.
    """

    def __init__(self, sink: List[Dict[str, Any]]):
        """
        Initializes the AuditLogWriter with a sink.

        The initial sequence number is determined by finding the maximum 'seq'
        value in the provided sink. If the sink is empty or contains no valid
        sequence numbers, the first sequence number will be 1.

        Args:
            sink: A list where audit records will be stored. This list may
                  already contain records, which will be scanned to determine
                  the next sequence number.

        Raises:
            TypeError: If the sink is not a list, if a record in the sink is
                       not a dictionary, or if a 'seq' value is not an integer.
            ValueError: If a record in the sink is missing the 'seq' key.
        """
        if not isinstance(sink, list):
            raise TypeError("sink must be a list")

        self._sink = sink
        self._lock = threading.Lock()
        self._next_seq = self._initialize_sequence_from_sink(sink)

    def _initialize_sequence_from_sink(self, sink: List[Dict[str, Any]]) -> int:
        """Determines the next sequence number from an existing sink."""
        if not sink:
            return 1

        max_seq = 0
        try:
            for record in sink:
                # This access will raise TypeError if a record is not a dict.
                seq = record['seq']
                if not isinstance(seq, int):
                    raise TypeError(
                        "all records in sink must have an integer 'seq' value"
                    )
                if seq > max_seq:
                    max_seq = seq
        except KeyError as e:
            raise ValueError("a record in sink is missing the 'seq' key") from e
        except TypeError as e:
            # This catches non-dict items in the sink.
            if "not subscriptable" in str(e):
                raise TypeError("all items in sink must be dictionaries") from e
            # Re-raise if it's the integer check from inside the loop.
            raise e

        return max_seq + 1

    def write(self, actor: str, action: str) -> Dict[str, Any]:
        """
        Creates and appends an audit record to the sink.

        The new record contains a monotonic sequence number, the actor, and
        the action. A shallow copy of the record is appended to the sink,
        and the original record is returned. This ensures that modifications
        to the returned dictionary do not affect the stored log record.

        Args:
            actor: The identifier of the user or system performing the action.
            action: A description of the action performed.

        Returns:
            A dictionary representing the newly created audit record.

        Raises:
            TypeError: If actor or action are not strings.
        """
        if not isinstance(actor, str):
            raise TypeError("actor must be a string")
        if not isinstance(action, str):
            raise TypeError("action must be a string")

        with self._lock:
            # Prepare the record inside the critical section.
            record = {
                'seq': self._next_seq,
                'actor': actor,
                'action': action,
            }

            # Append a copy to the sink to ensure the stored record is
            # immutable from the perspective of the caller.
            self._sink.append(record.copy())

            # Atomically increment for the next write.
            self._next_seq += 1

            return record
