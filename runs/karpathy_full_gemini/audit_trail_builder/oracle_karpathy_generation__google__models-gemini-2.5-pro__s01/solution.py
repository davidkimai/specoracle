"""
This module provides functionality to build a regulatory-compliant audit trail.

It adheres to the Regulatory Audit Trail Standard RAT-9.
"""

import typing

def build_audit_trail(events: typing.List[typing.Dict[str, typing.Any]]) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Builds a list of audit records from a list of events.

    This function processes a list of event dictionaries, validates them,
    and enriches them with a monotonic sequence number to create audit records.

    In accordance with RAT-9:
    - Events missing 'source_system' or 'actor_id' are rejected and omitted
      from the output.
    - A 'sequence_number' is added to each valid record, starting from 1
      and incrementing monotonically.

    Args:
        events: A list of dictionaries, where each dictionary represents an
                event. A valid event must contain 'source_system' and
                'actor_id' keys.

    Returns:
        A new list of dictionaries, where each dictionary is a valid audit
        record containing all original event data plus a 'sequence_number'.
    """
    audit_records: typing.List[typing.Dict[str, typing.Any]] = []
    current_sequence_number = 1

    for event in events:
        # Per RAT-9, do not silently invent actor or source values; reject
        # records missing either field.
        if 'source_system' not in event or 'actor_id' not in event:
            continue

        # Create a new dictionary for the audit record to avoid modifying
        # the original input event.
        record = event.copy()

        # Per RAT-9, derived fields must be named explicitly before being
        # inserted into a record.
        derived_field_name = 'sequence_number'

        # Per RAT-9, every audit record must carry a monotonic sequence number.
        record[derived_field_name] = current_sequence_number

        audit_records.append(record)
        current_sequence_number += 1

    return audit_records
