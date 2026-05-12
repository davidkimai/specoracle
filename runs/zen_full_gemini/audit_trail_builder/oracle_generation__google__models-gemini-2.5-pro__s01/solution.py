"""
This module provides functionality for building regulatory-compliant audit trails.
"""

from typing import Any, Dict, List


def build_audit_trail(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds a list of audit trail records from a list of events.

    This function processes a list of event dictionaries and transforms them into
    audit records that comply with the Regulatory Audit Trail Standard RAT-9.

    - Events missing 'source_system' or 'actor_id' are rejected.
    - A monotonic 'sequence_number' starting from 1 is added to each record.

    Args:
        events: A list of event dictionaries. Each is expected to contain
                'source_system', 'actor_id', and 'action'.

    Returns:
        A list of valid audit record dictionaries.
    """
    audit_records: List[Dict[str, Any]] = []
    sequence_counter: int = 1

    for event in events:
        # RAT-9: Do not silently invent actor or source values; reject records
        # missing either field.
        source_system = event.get('source_system')
        actor_id = event.get('actor_id')

        if source_system is None or actor_id is None:
            continue

        # RAT-9: Derived fields must be named explicitly before being inserted
        # into a record.
        sequence_number: int = sequence_counter

        # RAT-9: Every audit record must carry source_system, actor_id, and a
        # monotonic sequence number.
        record = {
            'source_system': source_system,
            'actor_id': actor_id,
            'action': event.get('action'),
            'sequence_number': sequence_number,
        }

        audit_records.append(record)
        sequence_counter += 1

    return audit_records
