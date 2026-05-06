"""audit_log_writer.py

Provides AuditLogWriter, a simple append-only audit log with monotonic sequence numbers.
"""

import copy


class AuditLogWriter:
    """Appends audit records to a caller-supplied sink list.

    Each record is a dict with keys: seq, actor, action.
    Sequence numbers start at 1 and increment by 1 for each write.
    The returned record is a copy of what was appended, so the two
    objects are never identical (no shared mutable state).
    """

    def __init__(self, sink: list) -> None:
        if not isinstance(sink, list):
            raise TypeError(f"sink must be a list, got {type(sink).__name__!r}")
        self._sink = sink
        self._seq = 0

    def write(self, actor: str, action: str) -> dict:
        if not isinstance(actor, str):
            raise TypeError(f"actor must be a str, got {type(actor).__name__!r}")
        if not isinstance(action, str):
            raise TypeError(f"action must be a str, got {type(action).__name__!r}")

        self._seq += 1
        record = {"seq": self._seq, "actor": actor, "action": action}
        self._sink.append(record)
        return copy.copy(record)
