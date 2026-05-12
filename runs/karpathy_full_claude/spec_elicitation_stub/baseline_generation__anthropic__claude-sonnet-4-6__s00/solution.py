def handle_underspecified(payload: dict) -> object:
    """
    Handle an underspecified payload.

    Currently specified behaviour:
        {'mode': 'echo', 'value': X}  ->  returns X

    All other input paths raise NotImplementedError to signal that the
    behaviour has not yet been specified rather than silently guessing.
    """
    if not isinstance(payload, dict):
        raise NotImplementedError(
            f"Behaviour for non-dict payload of type {type(payload)!r} is not specified."
        )

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise NotImplementedError(
                "Behaviour for 'echo' mode without a 'value' key is not specified."
            )
        return payload["value"]

    raise NotImplementedError(
        f"Behaviour for mode={mode!r} is not specified."
    )
