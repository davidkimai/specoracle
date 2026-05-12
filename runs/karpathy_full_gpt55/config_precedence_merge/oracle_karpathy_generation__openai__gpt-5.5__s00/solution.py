from copy import deepcopy


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    settings = _deep_merge(defaults, file_config)

    for key, value in env.items():
        if key.startswith("APP__"):
            path = [part.lower() for part in key[len("APP__"):].split("__")]
            _set_nested(settings, path, _parse_env_value(value))

    return settings


def _deep_merge(base: dict, override: dict) -> dict:
    result = deepcopy(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def _set_nested(target: dict, path: list[str], value) -> None:
    current = target

    for segment in path[:-1]:
        if not isinstance(current.get(segment), dict):
            current[segment] = {}
        current = current[segment]

    current[path[-1]] = value


def _parse_env_value(value: str):
    if value == "true":
        return True
    if value == "false":
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
        digits = value[1:]
    else:
        digits = value

    return bool(digits) and all("0" <= char <= "9" for char in digits)
