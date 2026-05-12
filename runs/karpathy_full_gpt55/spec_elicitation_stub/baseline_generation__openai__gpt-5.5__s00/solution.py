def handle_underspecified(payload: dict) -> object:
    if (
        isinstance(payload, dict)
        and set(payload.keys()) == {"mode", "value"}
        and payload["mode"] == "echo"
    ):
        return payload["value"]

    raise NotImplementedError("Behavior is only specified for {'mode': 'echo', 'value': X}.")
