from __future__ import annotations


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
    include_reason: bool = False,
) -> bool:
    role_permissions = matrix.get(role)
    if role_permissions is None:
        allowed = False
        reason = 'unknown_role'
    elif permission not in role_permissions:
        allowed = False
        reason = 'missing_permission'
    else:
        allowed = True
        reason = 'allowed'

    record: dict = {'role': role, 'permission': permission, 'allowed': allowed}
    if include_reason:
        record['reason'] = reason

    log.append(record)
    return allowed
