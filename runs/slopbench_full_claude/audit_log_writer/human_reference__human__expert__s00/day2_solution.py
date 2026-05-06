from __future__ import annotations
import hashlib


class AuditLogWriter:
    def __init__(self, sink: list[dict]) -> None:
        self._sink = sink
        self._sequence = 0

    def write(self, actor: str, action: str) -> dict:
        self._sequence += 1
        checksum = hashlib.sha256(
            f"{self._sequence}:{actor}:{action}".encode()
        ).hexdigest()
        record = {
            'sequence': self._sequence,
            'actor': actor,
            'action': action,
            'checksum': checksum,
        }
        self._sink.append(dict(record))
        return dict(record)
