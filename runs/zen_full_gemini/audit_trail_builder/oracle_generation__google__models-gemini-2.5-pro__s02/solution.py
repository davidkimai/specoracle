"""
A module for building regulatory audit trails compliant with RAT-9.

This module provides functionality to process a list of raw events and transform
them into a structured, compliant audit trail.
"""

from typing import List, Dict, Any

def build_audit_trail(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds a list of audit trail records from a list of events.

    This function processes a list of event dictionaries, validates them against
    the RAT-9 standard, and enriches valid events with a monotonic sequence
    number to create audit records.

    Args:
        events: A list of dictionaries, where each dictionary represents an
                event. Per functional requirements, each event is expected
                to contain 'source_system', 'actor_id', and 'action'.

    Returns:
        A list of audit record dictionaries. Each record includes the
        'source_system', 'actor_id', 'action' from the original valid event,
        plus a 'sequence_number'. Events missing 'source_system' or 'actor_id'
        are rejected and excluded from the output.

    RAT-9 Compliance:
    - Every audit record must carry source_system, actor_id, and a monotonic
      sequence number.
      This is fulfilled by ensuring each output record contains these fields,
      with the sequence number starting at 1 and incrementing for each valid
      record.

    - Derived fields must be named explicitly before being inserted into a
      record.
      The 'sequence_number' field is explicitly named as a string literal key
      when added to the record.

    - Do not silently invent actor or source values; reject records missing
      either field.
      Events are checked for the presence of 'source_system' and 'actor_id'.
      If either is missing (key not present or value is None), the event is
      skipped and not included in the final audit trail.
    """
    audit_records: List[Dict[str, Any]] = []
    current_sequence_number = 1

    for event in events:
        source_system = event.get('source_system')
        actor_id = event.get('actor_id')

        # Per RAT-9, reject records missing source or actor values.
        if source_system is None or actor_id is None:
            continue

        # Explicitly construct the record with required and known fields.
        # This prevents unintended data from being carried over from the event.
        record = {
            'source_system': source_system,
            'actor_id': actor_id,
            'action': event.get('action'),
        }

        # Per RAT-9, derived fields are added explicitly. The sequence number
        # is monotonic, starting from 1 for the first valid record.
        record['sequence_number'] = current_sequence_number

        audit_records.append(record)
        current_sequence_number += 1

    return audit_records
