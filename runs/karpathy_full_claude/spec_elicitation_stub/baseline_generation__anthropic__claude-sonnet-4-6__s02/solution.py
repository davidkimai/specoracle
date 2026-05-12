def handle_underspecified(payload: dict) -> object:
    """
    Handle underspecified payloads.

    The only fully specified behavior is:
        payload == {'mode': 'echo', 'value': X}  ->  returns X

    All other input paths raise NotImplementedError to avoid guessing
    at unspecified behavior.
    """
    if not isinstance(payload, dict):
        raise NotImplementedError(
            "Behavior for non-dict payloads is not specified."
        )

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise NotImplementedError(
                "Behavior for 'echo' mode without a 'value' key is not specified."
            )
        extra_keys = set(payload.keys()) - {"mode", "value"}
        if extra_keys:
            raise NotImplementedError(
                f"Behavior for 'echo' mode with extra keys {extra_keys!r} is not specified."
            )
        return payload["value"]

    raise NotImplementedError(
        f"Behavior for mode={mode!r} is not specified."
    )
