from threading import Lock


class AuditLogWriter:
    """Append audit log records to a provided list sink."""

    def __init__(self, sink: list[dict]) -> None:
        self._sink = sink
        self._next_sequence = 1
        self._lock = Lock()

    def write(self, actor: str, action: str) -> dict:
        """Append an audit record and return a distinct copy of it."""
        with self._lock:
            record = {
                "seq": self._next_sequence,
                "actor": actor,
                "action": action,
            }
            self._sink.append(record)
            self._next_sequence += 1
            return dict(record)
