"""
access_control_log module

Provides check_access for role-based access control with audit logging.
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

    Deny by default (i.e. when the role is absent or the permission is not
    listed for that role).  Every call is appended to *log* as a dict with
    keys: ``role``, ``permission``, ``allowed``, and ``timestamp``.

    Parameters
    ----------
    role:       The role whose access is being evaluated.
    permission: The permission being requested.
    matrix:     Mapping of role -> set of permitted permissions.
    log:        Mutable list that accumulates audit records (modified in-place).

    Returns
    -------
    bool: True if access is granted, False otherwise.
    """
    allowed: bool = permission in matrix.get(role, set())

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
    )

    return allowed
