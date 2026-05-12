class AuditLogWriter:
    """Write audit log records to a caller-provided list sink."""

    def __init__(self, sink: list[dict]):
        self._sink = sink
        self._next_sequence = 1

    def write(self, actor: str, action: str) -> dict:
        sequence = self._next_sequence
        self._next_sequence += 1

        record = {
            "sequence": sequence,
            "actor": actor,
            "action": action,
        }

        self._sink.append(record.copy())
        return record
