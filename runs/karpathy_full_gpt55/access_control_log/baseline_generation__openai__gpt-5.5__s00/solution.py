"""Access control decision helper with attempt logging."""

from __future__ import annotations

__all__ = ["check_access"]


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
) -> bool:
    """Return whether a role has a permission, logging the attempt first.

    Access is denied by default when the role is absent or the permission is not
    explicitly present in the role's permission set.
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
