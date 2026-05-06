def handle_underspecified(payload: dict) -> object:
    if not isinstance(payload, dict):
        raise TypeError(f"payload must be a dict, got {type(payload).__name__}")

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise KeyError("payload with mode 'echo' must contain 'value'")
        return payload["value"]

    if mode == "count":
        if "items" not in payload:
            raise KeyError("payload with mode 'count' must contain 'items'")
        items = payload["items"]
        if not isinstance(items, list):
            raise TypeError(f"'items' must be a list, got {type(items).__name__}")
        return len(items)

    raise NotImplementedError(f"No behavior specified for payload: {payload!r}")
