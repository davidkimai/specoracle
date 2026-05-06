import hashlib
import time


class AuditLogWriter:
    def __init__(self, sink: list) -> None:
        self._sink = sink
        self._sequence = 0

    def write(self, actor: str, action: str) -> dict:
        self._sequence += 1
        checksum_input = f"{self._sequence}:{actor}:{action}"
        checksum = hashlib.sha256(checksum_input.encode()).hexdigest()
        record = {
            "sequence": self._sequence,
            "actor": actor,
            "action": action,
            "timestamp": time.monotonic(),
            "checksum": checksum,
        }
        self._sink.append(dict(record))
        return record
