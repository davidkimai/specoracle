from copy import deepcopy


_PREFIX = "APP__"


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Return merged settings with precedence defaults < file_config < APP__ env."""
    settings = deepcopy(defaults)
    _deep_merge(settings, file_config)

    for key, value in env.items():
        if key.startswith(_PREFIX):
            path = [part.lower() for part in key[len(_PREFIX):].split("__")]
            _set_nested(settings, path, _parse_env_value(value))

    return settings


def _deep_merge(target: dict, source: dict) -> None:
    for key, value in source.items():
        if isinstance(target.get(key), dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = deepcopy(value)


def _set_nested(target: dict, path: list[str], value: object) -> None:
    current = target
    for part in path[:-1]:
        if not isinstance(current.get(part), dict):
            current[part] = {}
        current = current[part]
    current[path[-1]] = value


def _parse_env_value(value: str) -> object:
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _is_base10_integer(value):
        return int(value, 10)
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]

    return value


def _is_base10_integer(value: str) -> bool:
    if not value:
        return False
    if value[0] in "+-":
        return len(value) > 1 and value[1:].isdigit()
    return value.isdigit()
