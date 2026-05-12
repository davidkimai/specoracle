"""
A module for writing audit log records with monotonic sequence numbers.
"""

import threading
from typing import Any, Dict, List


class AuditLogWriter:
    """
    Writes audit log records to a given sink with monotonic sequence numbers.

    This class ensures that each record has a unique, strictly increasing
    sequence number, starting from 1. It is designed to be thread-safe.
    """

    def __init__(self, sink: List[Dict[str, Any]]):
        """
        Initializes the AuditLogWriter.

        Args:
            sink: A list where audit records (as dictionaries) will be
                  appended. This object is modified in place.
        """
        self._sink = sink
        self._sequence_number = 0
        self._lock = threading.Lock()

    def write(self, actor: str, action: str) -> Dict[str, Any]:
        """
        Creates an audit record, appends it to the sink, and returns it.

        The generated record contains a monotonic sequence number, the actor,
        and the action. The object appended to the sink is a distinct copy of
        the object returned by this method, ensuring they are not the same
        mutable object.

        Args:
            actor: The identifier of the user or system performing the action.
            action: A description of the action performed.

        Returns:
            A new dictionary representing the audit record that was created.
        """
        with self._lock:
            self._sequence_number += 1
            record = {
                "sequence_number": self._sequence_number,
                "actor": actor,
                "action": action,
            }
            # Per requirements, the appended and returned objects must not be
            # the same mutable object. We achieve this by appending a copy.
            self._sink.append(record.copy())
            return record
