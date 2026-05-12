from typing import Dict, List

class AuditLogWriter:
    """
    Writes audit log records to a sink with monotonic sequence numbers.
    """

    def __init__(self, sink: List[Dict]):
        """
        Initializes the AuditLogWriter.

        Args:
            sink: A list to which audit records will be appended.
        """
        self._sink = sink
        self._sequence_number = 0

    def write(self, actor: str, action: str) -> Dict:
        """
        Creates an audit record, appends it to the sink, and returns a copy.

        The sequence number is monotonically increasing, starting from 1.
        The returned record and the record appended to the sink are guaranteed
        to be distinct mutable objects.

        Args:
            actor: The identifier of the entity performing the action.
            action: A description of the action performed.

        Returns:
            A dictionary representing a copy of the created audit record.
        """
        self._sequence_number += 1
        record = {
            'sequence_number': self._sequence_number,
            'actor': actor,
            'action': action,
        }
        self._sink.append(record)
        return record.copy()
