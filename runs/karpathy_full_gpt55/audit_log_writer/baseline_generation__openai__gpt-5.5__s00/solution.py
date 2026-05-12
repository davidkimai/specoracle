from __future__ import annotations

from threading import Lock


class AuditLogWriter:
    """Append audit log records to a caller-provided list sink."""

    def __init__(self, sink: list[dict]):
        if not isinstance(sink, list):
            raise TypeError("sink must be a list")
        self._sink = sink
        self._next_sequence = 1
        self._lock = Lock()

    def write(self, actor: str, action: str) -> dict:
        """
        Append an audit record and return an equal but distinct record object.

        Sequence numbers are assigned monotonically, starting at 1 for the first
        record written by this writer.
        """
        with self._lock:
            sequence = self._next_sequence
            self._next_sequence += 1

            appended_record = {
                "seq": sequence,
                "actor": actor,
                "action": action,
            }
            returned_record = dict(appended_record)

            self._sink.append(appended_record)
            return returned_record
