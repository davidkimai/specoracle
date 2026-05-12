from typing import Any


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict[str, Any]],
) -> bool:
    allowed = False

    permissions = matrix.get(role)
    if permissions is not None and permission in permissions:
        allowed = True

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
