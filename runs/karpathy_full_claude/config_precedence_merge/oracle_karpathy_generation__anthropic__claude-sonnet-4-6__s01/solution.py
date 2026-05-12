import copy


def _parse_value(value: str):
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value, 10)
    except ValueError:
        pass
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return value


def _deep_merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _env_to_nested(env: dict) -> dict:
    result = {}
    prefix = "APP__"
    for key, value in env.items():
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        parsed = _parse_value(value)
        node = result
        for seg in segments[:-1]:
            if seg not in node or not isinstance(node[seg], dict):
                node[seg] = {}
            node = node[seg]
        node[segments[-1]] = parsed
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    result = _deep_merge(defaults, file_config)
    env_nested = _env_to_nested(env)
    result = _deep_merge(result, env_nested)
    return result
