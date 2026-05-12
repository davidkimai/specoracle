def check_access(role: str, permission: str, matrix: dict[str, set[str]], log: list[dict]) -> bool:
    permissions = matrix.get(role)
    allowed = permissions is not None and permission in permissions

    log.append(
        {
            "role": role,
            "permission": permission,
            "allowed": allowed,
        }
    )

    return allowed
