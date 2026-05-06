def handle_underspecified(payload: dict) -> object:
    if not isinstance(payload, dict):
        raise TypeError(f"payload must be a dict, got {type(payload).__name__}")

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise KeyError("payload with mode 'echo' must contain a 'value' key")
        return payload["value"]

    raise NotImplementedError(f"No behavior defined for payload: {payload!r}")
