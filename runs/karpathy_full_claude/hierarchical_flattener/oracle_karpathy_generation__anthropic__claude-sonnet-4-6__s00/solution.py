def flatten_paths(value: dict) -> dict:
    result = {}
    def _flatten(obj, prefix):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}.{k}" if prefix else k
                _flatten(v, new_key)
        else:
            result[prefix] = obj
    _flatten(value, "")
    return result
