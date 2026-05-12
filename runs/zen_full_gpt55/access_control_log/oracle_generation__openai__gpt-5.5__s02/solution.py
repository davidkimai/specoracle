"""Access control decision logging module."""

from typing import Any


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict[str, Any]],
) -> bool:
    """Return whether role has permission, logging the attempt before returning."""
    permissions = matrix.get(role)
    allowed = permission in permissions if permissions is not None else False

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
