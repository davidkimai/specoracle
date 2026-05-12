#
# audit_trail_builder
#
# A module for building regulatory audit trails in compliance with RAT-9.
#

import typing

# Type aliases for clarity in function signatures.
Event = typing.Dict[str, typing.Any]
AuditRecord = typing.Dict[str, typing.Any]


def build_audit_trail(events: typing.List[Event]) -> typing.List[AuditRecord]:
    """
    Builds a list of audit records from a list of events.

    This function processes a list of event dictionaries, validates them
    against RAT-9, and adds a monotonic sequence number to each valid event
    to create an audit record.

    In accordance with Regulatory Audit Trail Standard RAT-9:
    - Events without 'source_system' or 'actor_id' fields are rejected and
      excluded from the output.
    - A monotonic sequence number, starting from 1, is added to each
      valid record.
    - Derived fields, like the sequence number, are explicitly named in a
      local variable before being inserted into the record.

    Args:
        events: A list of dictionaries, where each dictionary represents
                an event. A valid event must contain 'source_system' and
                'actor_id' keys.

    Returns:
        A list of audit record dictionaries. Each valid record will
        contain all original event fields plus a 'sequence_number'.
        The list will be empty if no events are valid.
    """
    audit_trail: typing.List[AuditRecord] = []
    current_sequence_number = 1

    for event in events:
        # Per RAT-9, do not silently invent actor or source values; reject
        # records missing either field. Using .get() handles missing keys.
        source_system = event.get('source_system')
        actor_id = event.get('actor_id')

        if source_system is None or actor_id is None:
            continue  # Reject this event by skipping it.

        # Create a new dictionary to avoid modifying the original input event.
        record = event.copy()

        # Per RAT-9, every audit record must carry a monotonic sequence number.
        # Per RAT-9, derived fields must be named explicitly before insertion.
        derived_sequence_number: int = current_sequence_number
        record['sequence_number'] = derived_sequence_number

        audit_trail.append(record)

        # The sequence number increments only for valid records, ensuring
        # it remains monotonic in the final audit trail.
        current_sequence_number += 1

    return audit_trail
