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
    role       : The role identifier to check.
    permission : The permission identifier to check.
    matrix     : Mapping of role -> set of permitted permissions.
    log        : Mutable list to which the audit record is appended.

    Returns
    -------
    bool : True if access is allowed, False otherwise.

    ZT-2 guarantee: the log record is written unconditionally before the
    function returns, regardless of the decision.
    """
    allowed: bool = role in matrix and permission in matrix[role]

    record: dict = {
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }
    log.append(record)

    return allowed
