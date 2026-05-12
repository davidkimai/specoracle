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
        parts = [p.strip() for p in value.split(",")]
        return [p for p in parts if p]
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
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(prefix):
            continue
        remainder = raw_key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        parsed = _parse_value(raw_value)
        target = result
        for seg in segments[:-1]:
            if seg not in target or not isinstance(target[seg], dict):
                target[seg] = {}
            target = target[seg]
        target[segments[-1]] = parsed
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    merged = _deep_merge(defaults, file_config)
    env_nested = _env_to_nested(env)
    merged = _deep_merge(merged, env_nested)
    return merged
