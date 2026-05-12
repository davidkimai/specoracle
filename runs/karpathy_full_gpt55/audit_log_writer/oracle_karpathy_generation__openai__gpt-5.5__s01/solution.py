class AuditLogWriter:
    def __init__(self, sink: list[dict]):
        self.sink = sink
        self._sequence = 0

    def write(self, actor: str, action: str) -> dict:
        self._sequence += 1
        record = {
            "sequence": self._sequence,
            "actor": actor,
            "action": action,
        }
        self.sink.append(record)
        return dict(record)
