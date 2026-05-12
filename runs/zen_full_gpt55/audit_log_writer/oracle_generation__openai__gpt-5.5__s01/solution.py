class AuditLogWriter:
    """Write simple audit records to a caller-provided list."""

    def __init__(self, sink: list[dict]):
        if not isinstance(sink, list):
            raise TypeError("sink must be a list")

        self._sink = sink
        self._next_sequence = 1

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

        self._sink.append(record)
        return dict(record)
