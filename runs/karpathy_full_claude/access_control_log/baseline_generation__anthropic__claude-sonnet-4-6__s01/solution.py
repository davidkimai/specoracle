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

    Every call appends an entry to *log* with the keys:
        - timestamp (ISO-8601 UTC string)
        - role       (str)
        - permission (str)
        - allowed    (bool)

    Returns True if access is granted, False otherwise (deny by default).
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
