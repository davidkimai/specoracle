def flatten_paths(value: dict) -> dict[str, object]:
    """Flatten nested dictionaries into dot-separated path keys.

    Lists and all non-dict values are treated as leaves. Empty dictionaries do
    not produce output entries.
    """
    result: dict[str, object] = {}

    def visit(prefix: str, current: dict) -> None:
        for key, item in current.items():
            path = str(key) if not prefix else f"{prefix}.{key}"
            if isinstance(item, dict):
                visit(path, item)
            else:
                result[path] = item

    visit("", value)
    return result
