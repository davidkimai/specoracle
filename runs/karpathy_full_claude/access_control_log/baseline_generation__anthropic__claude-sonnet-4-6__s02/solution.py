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
    Check whether *role* has *permission* according to *matrix*.

    Every call is recorded in *log* as a dict with keys:
        - timestamp : ISO-8601 UTC string
        - role      : the role that was checked
        - permission: the permission that was checked
        - allowed   : bool result of the check

    Returns True if the role has the permission, False otherwise (deny by default).
    """
    allowed: bool = role in matrix and permission in matrix[role]

    log.append(
        {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
