from typing import Any


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict[str, Any]],
) -> bool:
    allowed = permission in matrix.get(role, set())

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
