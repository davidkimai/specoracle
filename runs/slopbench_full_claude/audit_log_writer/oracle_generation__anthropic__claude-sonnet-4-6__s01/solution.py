"""audit_log_writer.py

Provides AuditLogWriter, a simple append-only audit log with monotonic sequence numbers.
"""

import copy


class AuditLogWriter:
    """Appends audit records to a caller-supplied sink list.

    Each call to write() produces a record dict with keys:
        seq    – monotonic integer starting at 1
        actor  – the actor string
        action – the action string

    The record appended to the sink and the record returned are independent
    copies so neither can mutate the other.
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

        self._sink.append(copy.copy(record))
        return record
