def flatten_paths(value: dict) -> dict[str, object]:
    flattened: dict[str, object] = {}

    def walk(prefix: str, current: dict) -> None:
        for key, item in current.items():
            path = str(key) if not prefix else f"{prefix}.{key}"
            if isinstance(item, dict):
                walk(path, item)
            else:
                flattened[path] = item

    walk("", value)
    return flattened
