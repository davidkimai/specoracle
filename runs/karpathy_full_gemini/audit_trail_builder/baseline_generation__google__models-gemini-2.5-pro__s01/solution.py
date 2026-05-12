"""
This module provides functionality to build a sequenced audit trail from events.
"""

import collections.abc
from typing import Any, Dict, List

# Type alias for clarity, though not strictly necessary for this simple case.
Event = Dict[str, Any]
AuditRecord = Dict[str, Any]


def build_audit_trail(events: List[Event]) -> List[AuditRecord]:
    """
    Builds a sequenced audit trail from a list of raw events.

    This function iterates through a list of event dictionaries. It validates
    each event to ensure it contains both 'source_system' and 'actor_id' keys
    with non-None values. Events that fail this validation are rejected and
    excluded from the final audit trail.

    For each valid event, a new audit record is created by copying the event
    data and adding a 'sequence_number'. The sequence numbers start at 1 and
    are incremented for each subsequent valid event.

    Args:
        events: A list of dictionaries, where each dictionary represents an
                event to be processed.

    Returns:
        A new list of audit record dictionaries. Each record corresponds to a
        valid input event and includes an added 'sequence_number'. The order
        of records matches the order of valid events in the input list.

    Raises:
        TypeError: If the 'events' argument is not a list-like object.
    """
    if not isinstance(events, collections.abc.Sequence) or isinstance(events, str):
        raise TypeError("Input 'events' must be a list of dictionaries.")

    audit_trail: List[AuditRecord] = []
    sequence_number = 1

    for event in events:
        if not isinstance(event, dict):
            # To be robust, skip any items in the list that are not dictionaries.
            continue

        # The .get() method returns None if the key is missing.
        source_system = event.get('source_system')
        actor_id = event.get('actor_id')

        # Reject events if the required fields are missing or their value is None.
        if source_system is None or actor_id is None:
            continue

        # Create a new dictionary for the audit record to avoid modifying the
        # original event data.
        record = event.copy()
        record['sequence_number'] = sequence_number
        audit_trail.append(record)
        sequence_number += 1

    return audit_trail
