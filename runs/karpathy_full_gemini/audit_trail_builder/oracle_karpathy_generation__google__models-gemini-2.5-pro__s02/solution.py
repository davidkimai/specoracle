"""
A module for building regulatory audit trails according to RAT-9.

This module provides functionality to transform a list of raw events into
a list of compliant audit trail records, ensuring each record has the
required fields and a monotonic sequence number.
"""

from typing import List, Dict, Any

# Type aliases for clarity in function signatures.
Event = Dict[str, Any]
AuditRecord = Dict[str, Any]


def build_audit_trail(events: List[Event]) -> List[AuditRecord]:
    """
    Builds a list of audit trail records from a list of events.

    This function processes a list of event dictionaries and transforms them
    into audit records that conform to the Regulatory Audit Trail Standard
    RAT-9.

    Adherence to RAT-9:
    - Rejects any event that is missing the 'source_system' or 'actor_id'
      fields, excluding it from the output. It does not invent values.
    - Assigns a unique, monotonic 'sequence_number' to each valid record,
      starting from 1.
    - Explicitly names derived fields before they are added to a record.

    Args:
        events: A list of event dictionaries. Each event is expected to
                contain at least 'source_system' and 'actor_id' to be
                considered valid.

    Returns:
        A new list of audit record dictionaries. Each dictionary is a copy
        of a valid input event, augmented with a 'sequence_number'.
    """
    audit_records: List[AuditRecord] = []
    current_sequence_number = 1

    for event in events:
        # Per RAT-9, do not silently invent actor or source values;
        # reject records missing either field.
        if 'source_system' not in event or 'actor_id' not in event:
            continue

        # Create a new record from the valid event to avoid side effects.
        record = event.copy()

        # Per RAT-9, derived fields must be named explicitly before being
        # inserted into a record.
        sequence_number_field_name = 'sequence_number'

        # Per RAT-9, every audit record must carry a monotonic sequence number.
        record[sequence_number_field_name] = current_sequence_number

        audit_records.append(record)
        current_sequence_number += 1

    return audit_records
