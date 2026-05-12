def handle_underspecified(payload: dict) -> object:
    if (
        isinstance(payload, dict)
        and len(payload) == 2
        and payload.get("mode") == "echo"
        and "value" in payload
    ):
        return payload["value"]

    raise NotImplementedError("Behavior is not specified for this input.")
