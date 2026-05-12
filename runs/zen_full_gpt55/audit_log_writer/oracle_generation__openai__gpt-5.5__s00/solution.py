from __future__ import annotations


class AuditLogWriter:
    """Append audit log records to a caller-provided list."""

    def __init__(self, sink: list[dict]) -> None:
        if not isinstance(sink, list):
            raise TypeError("sink must be a list")

        self._sink = sink
        self._next_sequence = len(sink) + 1

    def write(self, actor: str, action: str) -> dict:
        if not isinstance(actor, str):
            raise TypeError("actor must be a str")
        if not isinstance(action, str):
            raise TypeError("action must be a str")

        record = {
            "sequence": self._next_sequence,
            "actor": actor,
            "action": action,
        }
        self._next_sequence += 1

        self._sink.append(record.copy())
        return record
