"""
Provides a class for writing audit logs with monotonic sequence numbers.
"""

class AuditLogWriter:
    """
    Writes audit log records to a sink with monotonic sequence numbers.

    The writer ensures that the record appended to the sink and the record
    returned to the caller are distinct mutable objects.
    """

    def __init__(self, sink: list[dict]):
        """
        Initializes the AuditLogWriter.

        Args:
            sink: A list-like object to which audit records will be appended.
                  This object is held by reference and will be mutated by the
                  write method.
        """
        self._sink = sink
        self._sequence_number: int = 0

    def write(self, actor: str, action: str) -> dict:
        """
        Creates, appends, and returns an audit log record.

        The record contains a monotonic sequence number (starting at 1), the
        actor, and the action. A copy of the record is appended to the sink,
        and the original record is returned.

        Args:
            actor: The identifier of the entity performing the action.
            action: A description of the action performed.

        Returns:
            A dictionary representing the created audit log record. The returned
            dictionary is a separate object from the one appended to the sink.
        """
        self._sequence_number += 1
        
        record = {
            "sequence_number": self._sequence_number,
            "actor": actor,
            "action": action,
        }

        # Per functional requirements, the appended record and the returned
        # record must not be the same mutable object. Appending a shallow
        # copy satisfies this constraint.
        self._sink.append(record.copy())

        return record
