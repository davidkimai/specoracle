import typing

def check_access(
    role: str,
    permission: str,
    matrix: typing.Dict[str, typing.Set[str]],
    log: typing.List[typing.Dict[str, typing.Union[str, bool]]]
) -> bool:
    """
    Checks if a role has a specific permission based on an access control matrix
    and logs the attempt.

    This function follows a "deny by default" policy. Access is only granted if
    the role is explicitly defined in the matrix and the permission is explicitly
    listed for that role.

    Args:
        role: The role attempting to perform an action.
        permission: The permission required for the action.
        matrix: A dictionary representing the access control list.
                Keys are role names (str), and values are sets of permissions (str).
        log: A list that will be mutated to store a log of this access attempt.
             Each log entry is a dictionary containing 'role', 'permission',
             and 'allowed'.

    Returns:
        True if access is granted, False otherwise.
    """
    # Deny by default. Access is only granted if the role is found and the
    # permission is in the role's permission set.
    permissions_for_role = matrix.get(role, set())
    allowed = permission in permissions_for_role

    # Log every attempt before returning the decision.
    log_entry: typing.Dict[str, typing.Union[str, bool]] = {
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }
    log.append(log_entry)

    return allowed
