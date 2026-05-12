"""
A module for building regulatory-compliant audit trails.
"""

from typing import Any, Dict, List

def build_audit_trail(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds a list of audit trail records from a list of events.

    This function processes a list of event dictionaries and transforms them into
    audit records compliant with the Regulatory Audit Trail Standard RAT-9.

    Each valid event is converted into an audit record with a monotonic sequence
    number. Events that do not meet the minimum requirements (missing
    'source_system' or 'actor_id') are rejected and excluded from the output.

    Args:
        events: A list of event dictionaries. Each dictionary represents an
                event and is expected to contain at least 'source_system'
                and 'actor_id' keys.

    Returns:
        A new list of audit trail record dictionaries. Each record includes
        all fields from the original event plus a 'sequence_number' field.
        The sequence numbers start at 1 and are monotonic.
    """
    audit_trail: List[Dict[str, Any]] = []
    current_sequence_number = 1

    for event in events:
        # RAT-9: Do not silently invent actor or source values; reject records
        # missing either field.
        if 'source_system' not in event or 'actor_id' not in event:
            continue

        # Create a new record from the event to avoid modifying the input.
        record = event.copy()

        # RAT-9: Derived fields must be named explicitly before being inserted
        # into a record.
        sequence_number_field = 'sequence_number'

        # RAT-9: Every audit record must carry source_system, actor_id, and a
        # monotonic sequence number.
        record[sequence_number_field] = current_sequence_number

        audit_trail.append(record)
        current_sequence_number += 1

    return audit_trail
