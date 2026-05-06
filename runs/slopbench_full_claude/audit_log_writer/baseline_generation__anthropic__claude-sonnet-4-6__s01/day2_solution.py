import hashlib
import time


class AuditLogWriter:
    def __init__(self, sink: list) -> None:
        self._sink = sink
        self._sequence = 0

    @staticmethod
    def _compute_checksum(sequence: int, actor: str, action: str) -> str:
        payload = f"{sequence}:{actor}:{action}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def write(self, actor: str, action: str) -> dict:
        self._sequence += 1
        checksum = self._compute_checksum(self._sequence, actor, action)
        record = {
            "sequence": self._sequence,
            "actor": actor,
            "action": action,
            "timestamp": time.monotonic(),
            "checksum": checksum,
        }
        self._sink.append(dict(record))
        return record
