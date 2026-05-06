"""
access_control_log.py

Implements check_access with logging of every access attempt.
"""

from datetime import datetime, timezone


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """
    Determine whether *role* holds *permission* according to *matrix*.

    Every call appends an entry to *log* with the keys:
        - timestamp : ISO-8601 UTC string
        - role      : the role that was checked
        - permission: the permission that was checked
        - allowed   : bool result of the check

    Deny by default (i.e. when the role is absent or lacks the permission).

    Parameters
    ----------
    role:       The role to check.
    permission: The permission to verify.
    matrix:     Mapping of role -> set of granted permissions.
    log:        Mutable list; an audit record is appended before returning.

    Returns
    -------
    bool – True if access is granted, False otherwise.
    """
    allowed: bool = permission in matrix.get(role, set())

    log.append(
        {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
