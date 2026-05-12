class AuditLogWriter:
    def __init__(self, sink: list[dict]):
        self._sink = sink
        self._next_seq = 1

    def write(self, actor: str, action: str) -> dict:
        record = {"seq": self._next_seq, "actor": actor, "action": action}
        self._next_seq += 1
        self._sink.append(record.copy())
        return record
