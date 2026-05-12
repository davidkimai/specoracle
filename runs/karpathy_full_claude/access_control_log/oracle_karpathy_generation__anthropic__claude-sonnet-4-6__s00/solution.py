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
    """Check whether *role* holds *permission* according to *matrix*.

    The result (allowed or denied) is appended to *log* before being
    returned.  Denial is the default when the role or permission is
    absent from the matrix.

    Parameters
    ----------
    role:       The role whose access is being evaluated.
    permission: The permission being requested.
    matrix:     Mapping from role name to the set of granted permissions.
    log:        Mutable list to which the audit record is appended.

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
