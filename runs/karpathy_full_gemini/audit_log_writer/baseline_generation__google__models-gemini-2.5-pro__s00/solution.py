# a_autogen_module_for_task_audit_log_writer
#
# Copyright (c) 2024, The AuditLogWriter Authors.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
"""
A thread-safe audit log writer that appends records with monotonic sequence
numbers to a sink.
"""

import threading
from typing import Any, Dict, List


class AuditLogWriter:
    """
    Writes audit log records to a sink with monotonic sequence numbers.

    This class ensures that each record has a unique, monotonically increasing
    sequence number, starting from 1. It is designed to be thread-safe,
    allowing multiple threads to write to the same sink without race
    conditions on the sequence number or the sink itself.

    Attributes:
        _sink (List[Dict[str, Any]]): The destination list for audit records.
        _sequence_number (int): The last used sequence number.
        _lock (threading.Lock): A lock to ensure thread-safe operations.
    """

    def __init__(self, sink: List[Dict[str, Any]]):
        """
        Initializes the AuditLogWriter with a given sink.

        Args:
            sink: A list-like object to which audit records will be appended.
                  This object must be a list.

        Raises:
            TypeError: If the provided sink is not a list.
        """
        if not isinstance(sink, list):
            raise TypeError("The 'sink' must be a list.")
        self._sink = sink
        self._sequence_number = 0
        self._lock = threading.Lock()

    def write(self, actor: str, action: str) -> Dict[str, Any]:
        """
        Creates and appends an audit log record to the sink.

        This method generates a new record containing a unique sequence number,
        the actor, and the action. The record is appended to the sink provided
        during initialization. The operation is atomic to ensure thread safety.

        Args:
            actor: The identifier of the entity performing the action.
            action: A description of the action being performed.

        Returns:
            A shallow copy of the record that was appended to the sink.
            The returned dictionary is a distinct object from the one stored
            in the sink to prevent unintended mutations of the log.
        """
        with self._lock:
            self._sequence_number += 1
            record = {
                "sequence": self._sequence_number,
                "actor": actor,
                "action": action,
            }
            self._sink.append(record)
            # Per functional requirements, the returned record must not be the
            # same mutable object as the one appended to the sink.
            return record.copy()
