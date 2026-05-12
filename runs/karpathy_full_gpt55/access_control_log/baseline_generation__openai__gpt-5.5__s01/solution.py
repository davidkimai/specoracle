"""Access control decision helper with audit logging."""

from __future__ import annotations


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """
    Check whether a role has a permission and log the access attempt.

    Access is denied by default when the role is absent or the permission is not
    explicitly present in the role's permission set.

    Args:
        role: The role requesting access.
        permission: The permission being requested.
        matrix: Mapping of roles to explicitly granted permissions.
        log: Mutable list that receives an audit entry for this attempt.

    Returns:
        True if access is explicitly granted, otherwise False.
    """
    allowed = permission in matrix.get(role, set())

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed


__all__ = ["check_access"]
