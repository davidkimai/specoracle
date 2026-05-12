"""
A module for writing audit log records.
"""

import typing

class AuditLogWriter:
    """
    Writes audit records with monotonic sequence numbers to a sink.

    Each record is a dictionary containing a sequence number, an actor, and an
    action. The writer ensures that sequence numbers are unique and
    monotonically increasing for its lifetime.
    """

    def __init__(self, sink: list[dict]) -> None:
        """
        Initializes the AuditLogWriter with a list-like sink.

        Args:
            sink: A list where audit records will be appended. This object
                  is mutated by the `write` method.

        Raises:
            TypeError: If sink is not a list.
        """
        if not isinstance(sink, list):
            raise TypeError("sink must be a list")
        self._sink = sink
        self._sequence_number = 0

    def write(self, actor: str, action: str) -> dict:
        """
        Creates, appends, and returns an audit record.

        The record is appended to the sink provided during initialization.
        The sequence number is incremented atomically for each call.

        Args:
            actor: The identifier of the actor performing the action.
            action: A description of the action being performed.

        Returns:
            A copy of the audit record that was written. The returned object
            is a new dictionary, distinct from the one stored in the sink,
            to prevent accidental mutation of the audit log.

        Raises:
            TypeError: If actor or action are not strings.
            ValueError: If actor or action are empty strings.
        """
        _validate_record_fields(actor, action)

        self._sequence_number += 1

        record = {
            "sequence_number": self._sequence_number,
            "actor": actor,
            "action": action,
        }

        self._sink.append(record)

        return record.copy()


def _validate_record_fields(actor: str, action: str) -> None:
    """
    Validates the core fields of an audit record.

    Helper to ensure actor and action are non-empty strings.

    Raises:
        TypeError: If actor or action are not strings.
        ValueError: If actor or action are empty strings.
    """
    if not isinstance(actor, str):
        raise TypeError("actor must be a string")
    if not isinstance(action, str):
        raise TypeError("action must be a string")

    if not actor:
        raise ValueError("actor must not be an empty string")
    if not action:
        raise ValueError("action must not be an empty string")
