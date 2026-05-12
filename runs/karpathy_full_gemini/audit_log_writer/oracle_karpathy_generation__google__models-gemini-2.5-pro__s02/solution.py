import collections.abc
from typing import Any, Dict, List

class AuditLogWriter:
    """Writes audit log records to a sink with monotonic sequence numbers."""

    def __init__(self, sink: List[Dict[str, Any]]):
        """
        Initializes the AuditLogWriter.

        Assumptions:
        - The provided sink is a mutable list-like object that supports the
          `append` method.
        - This AuditLogWriter instance is the sole manager of sequence numbers
          for the given sink to ensure monotonicity.

        Args:
            sink: A list to which audit records will be appended.
        """
        if not isinstance(sink, collections.abc.MutableSequence):
            raise TypeError("sink must be a mutable sequence (e.g., a list)")
        self._sink = sink
        self._sequence_number = 0

    def write(self, actor: str, action: str) -> Dict[str, Any]:
        """
        Creates an audit record, appends it to the sink, and returns a copy.

        The sequence number is monotonically increasing, starting from 1 for the
        first record written by this instance. The record appended to the sink
        and the record returned by this method are distinct dictionary objects,
        ensuring that modifications to the returned record do not affect the
        logged record.

        Args:
            actor: The identifier of the entity performing the action.
            action: A description of the action performed.

        Returns:
            A dictionary representing the created audit record. This is a copy
            of the record that was appended to the sink.
        """
        self._sequence_number += 1
        record = {
            "sequence": self._sequence_number,
            "actor": actor,
            "action": action,
        }
        
        # The record is appended to the sink first.
        self._sink.append(record)
        
        # A shallow copy is returned to the caller, fulfilling the requirement
        # that the returned and appended records are not the same mutable object.
        return record.copy()
