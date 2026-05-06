"""audit_log_writer.py

Provides AuditLogWriter, a simple append-only audit log with monotonic sequence
numbers.
"""

import datetime


class AuditLogWriter:
    """Appends immutable audit records to a caller-supplied sink list."""

    def __init__(self, sink: list) -> None:
        if not isinstance(sink, list):
            raise TypeError(f"sink must be a list, got {type(sink).__name__!r}")
        self._sink = sink
        self._sequence = 0

    def write(self, actor: str, action: str) -> dict:
        """Append an audit record and return a copy of it.

        Parameters
        ----------
        actor:  identity of the entity performing the action
        action: description of the action performed

        Returns
        -------
        A dict copy of the appended record (not the same object as what is
        stored in the sink).
        """
        if not isinstance(actor, str):
            raise TypeError(f"actor must be a str, got {type(actor).__name__!r}")
        if not isinstance(action, str):
            raise TypeError(f"action must be a str, got {type(action).__name__!r}")

        self._sequence += 1

        record = {
            "sequence": self._sequence,
            "actor": actor,
            "action": action,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

        self._sink.append(dict(record))
        return record
