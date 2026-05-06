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
    include_reason: bool = False,
) -> bool:
    """
    Check whether *role* has *permission* according to *matrix*.

    Every call appends an entry to *log* with the keys:
        - timestamp  (ISO-8601 UTC string)
        - role       (str)
        - permission (str)
        - allowed    (bool)
        - reason     (str, only present when include_reason=True)
                     One of 'allowed', 'unknown_role', or 'missing_permission'.

    Returns True if access is granted, False otherwise (deny by default).
    """
    if role not in matrix:
        allowed = False
        reason = "unknown_role"
    elif permission not in matrix[role]:
        allowed = False
        reason = "missing_permission"
    else:
        allowed = True
        reason = "allowed"

    entry: dict = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }

    if include_reason:
        entry["reason"] = reason

    log.append(entry)

    return allowed
