def check_access(role: str, permission: str, matrix: dict[str, set[str]], log: list[dict]) -> bool:
    allowed = False

    permissions = matrix.get(role)
    if permissions is not None:
        allowed = permission in permissions

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
