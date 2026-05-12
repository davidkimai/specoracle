class AuditLogWriter:
    def __init__(self, sink: list[dict]):
        if not isinstance(sink, list):
            raise TypeError("sink must be a list of dictionaries")
        if any(not isinstance(record, dict) for record in sink):
            raise TypeError("sink must contain only dictionaries")

        self._sink = sink
        self._next_sequence = 1

    def write(self, actor: str, action: str) -> dict:
        if not isinstance(actor, str):
            raise TypeError("actor must be a string")
        if not isinstance(action, str):
            raise TypeError("action must be a string")

        record = {
            "sequence": self._next_sequence,
            "actor": actor,
            "action": action,
        }
        self._next_sequence += 1

        self._sink.append(dict(record))
        return dict(record)
