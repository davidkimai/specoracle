"""
access_control_log.py

Implements check_access following Zero-Trust Audit Principle ZT-2:
every access attempt is logged (role, permission, allowed) before the
decision is returned, with no short-circuit path that bypasses the log.
"""


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """Check whether *role* has *permission* according to *matrix*.

    Deny by default (when the role is absent or the permission is not in its
    set).  Every attempt – allowed or denied – is appended to *log* before
    the boolean result is returned.

    Parameters
    ----------
    role:       The role string to look up.
    permission: The permission string to check.
    matrix:     Mapping of role → set of permitted permission strings.
    log:        Mutable list; a record dict is appended on every call.

    Returns
    -------
    bool: True if access is allowed, False otherwise.
    """
    allowed: bool = permission in matrix.get(role, set())

    log.append({
        "role": role,
        "permission": permission,
        "allowed": allowed,
    })

    return allowed
