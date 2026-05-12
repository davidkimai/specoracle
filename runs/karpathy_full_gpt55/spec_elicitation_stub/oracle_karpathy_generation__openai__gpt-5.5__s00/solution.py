def handle_underspecified(payload: dict) -> object:
    if (
        isinstance(payload, dict)
        and set(payload) == {"mode", "value"}
        and payload["mode"] == "echo"
    ):
        return payload["value"]

    raise NotImplementedError("Only {'mode': 'echo', 'value': X} is implemented")
