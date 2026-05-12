#
# Copyright (c) 2024, Python Secure Synthesis Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
A module for access control with mandatory logging.
"""

from typing import Dict, List, Set, Any

def check_access(
    role: str,
    permission: str,
    matrix: Dict[str, Set[str]],
    log: List[Dict[str, Any]]
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function adheres to Zero-Trust Audit Principle ZT-2:
    - Every access attempt is logged before returning, whether allowed or denied.
    - No short-circuit return bypasses the log write.
    - Log records include role, permission, and the outcome (allowed).

    Args:
        role: The role attempting the access.
        permission: The permission being requested.
        matrix: An access control matrix mapping roles to sets of permissions.
        log: A list to which log records will be appended.

    Returns:
        True if access is allowed, False otherwise.
    """
    # Deny by default. Determine if the requested permission is granted to the role.
    # The .get() method safely handles cases where the role is not in the matrix,
    # returning an empty set and ensuring the check results in False.
    permissions_for_role = matrix.get(role, set())
    allowed = permission in permissions_for_role

    # Create the log record for this access attempt.
    # This must happen after the decision is made and before returning.
    log_record: Dict[str, Any] = {
        'role': role,
        'permission': permission,
        'allowed': allowed,
    }
    log.append(log_record)

    # Return the final decision only after the attempt has been logged.
    return allowed
