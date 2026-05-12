#
# Copyright (c) 2023-present, Trail of Bits, Inc.
# All rights reserved.
#
# This source code is licensed in accordance with the terms specified in
# the LICENSE file found in the root directory of this source tree.
#

"""
A module for writing audit log records with monotonic sequence numbers.

This module provides an `AuditLogWriter` class that appends structured log
records to a provided sink. It ensures that each record has a unique,
monotonically-increasing sequence number.
"""

from typing import Any, Dict, List

# A type alias for a single audit record.
AuditRecord = Dict[str, Any]

# A type alias for the list that audit records are written to.
AuditSink = List[AuditRecord]


def _get_next_sequence_number(sink: AuditSink) -> int:
    """
    Calculates the next sequence number based on the sink's content.

    This function inspects the provided sink to find the highest existing
    sequence number and determines the next one in the sequence.

    Args:
        sink: A list of dictionary records.

    Returns:
        The next integer sequence number to be used.

    Raises:
        ValueError: If a record in the sink is malformed (e.g., missing 'seq',
                    non-positive 'seq', or non-integer 'seq').
        TypeError: If an item in the sink is not a dictionary.
    """
    if not sink:
        return 1

    max_seq = 0
    for i, record in enumerate(sink):
        if not isinstance(record, dict):
            raise TypeError(f"Sink item at index {i} is not a dictionary.")

        seq = record.get("seq")

        if not isinstance(seq, int):
            raise ValueError(
                f"Sink item at index {i} has a missing or non-integer 'seq' key."
            )

        if seq <= 0:
            raise ValueError(
                f"Sink item at index {i} has a non-positive 'seq' value: {seq}."
            )

        max_seq = max(max_seq, seq)

    return max_seq + 1


def _validate_log_parameter(value: str, name: str) -> None:
    """
    Validates that a parameter for a log entry is a non-empty string.

    Args:
        value: The parameter's value.
        name: The parameter's name, for use in error messages.

    Raises:
        TypeError: If the value is not a string.
        ValueError: If the value is an empty string.
    """
    if not isinstance(value, str):
        raise TypeError(f"{name.capitalize()} must be a string.")
    if not value:
        raise ValueError(f"{name.capitalize()} cannot be empty.")


class AuditLogWriter:
    """
    Writes audit log records to a list-based sink with monotonic sequence numbers.
    """

    def __init__(self, sink: AuditSink):
        """
        Initializes the AuditLogWriter.

        The writer's sequence number is initialized based on the existing
        contents of the sink, ensuring monotonicity.

        Args:
            sink: A list-like object where audit records will be appended.
                  The writer holds a reference to this object and will mutate it.

        Raises:
            TypeError: If the sink is not a list or contains non-dict items.
            ValueError: If the sink contains malformed records.
        """
        if not isinstance(sink, list):
            raise TypeError("Sink must be a list of dictionaries.")

        self._sink = sink
        self._next_seq = _get_next_sequence_number(sink)

    def write(self, actor: str, action: str) -> AuditRecord:
        """
        Creates and appends an audit record to the sink.

        The record contains a monotonic sequence number, the actor, and the action.
        The internal sequence number is incremented after each write.

        Args:
            actor: The identifier of the entity performing the action.
            action: A description of the action performed.

        Returns:
            A shallow copy of the record that was appended to the sink. The
            returned dictionary is a separate object from the one in the sink.

        Raises:
            TypeError: If actor or action are not strings.
            ValueError: If actor or action are empty strings.
        """
        _validate_log_parameter(actor, "actor")
        _validate_log_parameter(action, "action")

        record: AuditRecord = {
            "seq": self._next_seq,
            "actor": actor,
            "action": action,
        }

        self._sink.append(record)
        self._next_seq += 1

        return record.copy()
