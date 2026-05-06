"""
access_control_log.py

Zero-Trust access control with mandatory audit logging (ZT-2).
Every access attempt is logged before the decision is returned.
"""


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """
    Check whether *role* holds *permission* according to *matrix*.

    Parameters
    ----------
    role:       The role whose access is being evaluated.
    permission: The permission being requested.
    matrix:     Mapping of role -> set of granted permissions.
    log:        Mutable list; a record is appended before every return.

    Returns
    -------
    bool: True if access is allowed, False otherwise (deny-by-default).
    """
    allowed = permission in matrix.get(role, set())

    # ZT-2: log must be written before returning, no short-circuit bypass.
    log.append({
        "role": role,
        "permission": permission,
        "allowed": allowed,
    })

    return allowed
