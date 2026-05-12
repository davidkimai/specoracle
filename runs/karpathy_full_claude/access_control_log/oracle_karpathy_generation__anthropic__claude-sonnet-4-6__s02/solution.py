"""
access_control_log.py

Implements check_access following Zero-Trust Audit Principle ZT-2:
every access attempt is logged before returning, whether allowed or denied.
"""


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """
    Check whether *role* holds *permission* according to *matrix*.

    The decision is appended to *log* as a dict with keys
    ``role``, ``permission``, and ``allowed`` before the function returns.

    Deny by default (i.e. when the role is absent from the matrix or
    the permission is not in the role's set).

    Parameters
    ----------
    role:       The role string to look up.
    permission: The permission string to check.
    matrix:     Mapping of role -> set of permitted permission strings.
    log:        Mutable list; a record is appended on every call.

    Returns
    -------
    bool: True if access is allowed, False otherwise.
    """
    allowed: bool = permission in matrix.get(role, set())

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
