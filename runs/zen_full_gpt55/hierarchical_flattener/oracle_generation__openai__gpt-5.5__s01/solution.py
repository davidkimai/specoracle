_SEPARATOR = "."


def flatten_paths(value: dict) -> dict[str, object]:
    """Flatten nested dictionaries into a new dictionary with dot-path keys."""
    if not isinstance(value, dict):
        raise TypeError("flatten_paths() requires a dict")

    flattened: dict[str, object] = {}
    _flatten_dict(value, "", flattened, set())
    return flattened


def _flatten_dict(
    value: dict,
    prefix: str,
    flattened: dict[str, object],
    active_ids: set[int],
) -> None:
    value_id = id(value)
    if value_id in active_ids:
        raise ValueError(f"cycle detected while flattening path {prefix!r}")

    active_ids.add(value_id)
    try:
        if not value:
            if prefix:
                _store_leaf(flattened, prefix, value)
            return

        for key, item in value.items():
            _validate_key(key)
            path = _join_path(prefix, key)

            if isinstance(item, dict):
                _flatten_dict(item, path, flattened, active_ids)
                continue

            _store_leaf(flattened, path, item)
    finally:
        active_ids.remove(value_id)


def _validate_key(key: object) -> None:
    if not isinstance(key, str):
        raise TypeError(f"dict keys must be str, got {type(key).__name__}")

    if key == "":
        raise ValueError("dict keys must not be empty strings")


def _join_path(prefix: str, key: str) -> str:
    if not prefix:
        return key
    return f"{prefix}{_SEPARATOR}{key}"


def _store_leaf(flattened: dict[str, object], path: str, value: object) -> None:
    if path in flattened:
        raise ValueError(f"flattened path collision at {path!r}")

    flattened[path] = value
