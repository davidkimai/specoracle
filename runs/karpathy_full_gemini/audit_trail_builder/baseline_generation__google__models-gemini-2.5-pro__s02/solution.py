"""
This module provides functionality to build a sequenced audit trail from events.
"""

from typing import List, Dict, Any

def build_audit_trail(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds a sequenced audit trail from a list of raw event dictionaries.

    This function processes a list of event dictionaries. It validates each event
    to ensure it contains the required 'source_system' and 'actor_id' keys.
    Events that fail this validation are rejected and excluded from the output.

    For each valid event, a 'sequence_number' is added, starting from 1 and
    incrementing for each subsequent valid event. The original order of valid
    events is preserved.

    Args:
        events: A list of dictionaries, where each dictionary represents an
                event. An event may contain various keys, but 'source_system'
                and 'actor_id' are mandatory for it to be considered valid.

    Returns:
        A new list of dictionaries representing the audit trail records.
        Each record is a copy of a valid input event, augmented with a
        'sequence_number'. The list is empty if no valid events are found.
    """
    audit_trail_records = []
    current_sequence_number = 1

    for event in events:
        # Validate that the event contains the required keys.
        if 'source_system' not in event or 'actor_id' not in event:
            continue  # Reject the event by skipping it.

        # Create a new dictionary for the audit record to avoid modifying
        # the original input event data.
        record = event.copy()
        record['sequence_number'] = current_sequence_number
        audit_trail_records.append(record)

        # Increment the sequence number for the next valid event.
        current_sequence_number += 1

    return audit_trail_records
