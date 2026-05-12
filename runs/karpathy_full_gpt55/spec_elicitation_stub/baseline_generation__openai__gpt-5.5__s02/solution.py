def handle_underspecified(payload: dict) -> object:
    """
    Handle the single specified input shape.

    Specified behavior:
        {'mode': 'echo', 'value': X} -> X

    Any other input is intentionally unsupported.
    """
    if (
        isinstance(payload, dict)
        and set(payload.keys()) == {"mode", "value"}
        and payload["mode"] == "echo"
    ):
        return payload["value"]

    raise NotImplementedError("Unspecified input path")
