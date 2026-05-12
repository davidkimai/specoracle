def flatten_paths(value: dict) -> dict[str, object]:
    """Flatten nested dictionaries into dot-separated path keys.

    Assumptions:
    - Dictionary keys are intended to be path components.
    - Lists and all non-dictionary values are leaves.
    - Empty dictionaries contribute no output entries.
    """
    result: dict[str, object] = {}

    def walk(prefix: str, current: dict) -> None:
        for key, item in current.items():
            path = str(key) if not prefix else f"{prefix}.{key}"
            if isinstance(item, dict):
                walk(path, item)
            else:
                result[path] = item

    walk("", value)
    return result
