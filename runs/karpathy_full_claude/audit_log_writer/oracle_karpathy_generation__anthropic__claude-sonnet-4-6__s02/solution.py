import time


class AuditLogWriter:
    def __init__(self, sink: list):
        self._sink = sink
        self._seq = 0

    def write(self, actor: str, action: str) -> dict:
        self._seq += 1
        record = {
            "seq": self._seq,
            "actor": actor,
            "action": action,
            "timestamp": time.time(),
        }
        self._sink.append(dict(record))
        return record
