from copy import deepcopy
import re


_INT_RE = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    result = deepcopy(defaults)
    _deep_merge(result, file_config)

    for key, value in env.items():
        if key.startswith("APP__"):
            path = [part.lower() for part in key[len("APP__"):].split("__")]
            _set_nested(result, path, _parse_env_value(value))

    return result


def _deep_merge(target: dict, source: dict) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
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
    if value == "true":
        return True
    if value == "false":
        return False
    if _INT_RE.fullmatch(value):
        return int(value, 10)
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return value
