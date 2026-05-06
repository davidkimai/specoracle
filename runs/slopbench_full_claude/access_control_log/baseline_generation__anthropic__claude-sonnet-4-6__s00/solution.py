"""
access_control_log module

Provides check_access for role-based permission checking with audit logging.
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

    Every call appends an entry to *log* containing:
        - role       : the role string supplied
        - permission : the permission string supplied
        - allowed    : the boolean decision
        - timestamp  : ISO-8601 UTC timestamp

    Returns True if access is granted, False otherwise (deny by default).
    """
    allowed: bool = False

    if role in matrix and permission in matrix[role]:
        allowed = True

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
    )

    return allowed
