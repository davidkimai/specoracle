from __future__ import annotations

__all__ = ["check_access"]


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """
    Check whether a role has a permission and record the access attempt.

    Access is denied by default: a role is allowed only when it exists in the
    matrix and its permission set contains the requested permission.
    """
    permissions = matrix.get(role)
    allowed = isinstance(permissions, set) and permission in permissions

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
