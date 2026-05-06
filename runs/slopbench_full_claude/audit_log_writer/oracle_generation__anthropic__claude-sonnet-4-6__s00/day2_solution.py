"""audit_log_writer.py

Provides AuditLogWriter, a simple append-only audit log with monotonic sequence numbers.
"""

import copy
import hashlib


class AuditLogWriter:
    """Appends audit records to a caller-supplied sink list.

    Each record is a dict with keys: seq, actor, action, checksum.
    Sequence numbers start at 1 and increment by 1 for each write.
    The checksum is an SHA-256 hex digest computed over seq, actor, and action
    before the checksum field is added to the record.
    The returned record is a copy of what was appended, so the two
    objects are never identical (no shared mutable state).
    """

    def __init__(self, sink: list) -> None:
        if not isinstance(sink, list):
            raise TypeError(f"sink must be a list, got {type(sink).__name__!r}")
        self._sink = sink
        self._seq = 0

    @staticmethod
    def _compute_checksum(seq: int, actor: str, action: str) -> str:
        payload = f"{seq}:{actor}:{action}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def write(self, actor: str, action: str) -> dict:
        if not isinstance(actor, str):
            raise TypeError(f"actor must be a str, got {type(actor).__name__!r}")
        if not isinstance(action, str):
            raise TypeError(f"action must be a str, got {type(action).__name__!r}")

        self._seq += 1
        checksum = self._compute_checksum(self._seq, actor, action)
        record = {"seq": self._seq, "actor": actor, "action": action, "checksum": checksum}
        self._sink.append(record)
        return copy.copy(record)
