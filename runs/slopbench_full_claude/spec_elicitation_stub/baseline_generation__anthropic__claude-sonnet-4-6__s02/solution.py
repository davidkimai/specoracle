def handle_underspecified(payload: dict) -> object:
    """
    Handle underspecified payloads.

    Specified behaviour:
        payload == {'mode': 'echo', 'value': X}  ->  return X

    All other inputs raise NotImplementedError.
    """
    if not isinstance(payload, dict):
        raise NotImplementedError(
            f"Unspecified behaviour for non-dict payload: {payload!r}"
        )

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise NotImplementedError(
                "Unspecified behaviour for 'echo' mode without 'value' key."
            )
        # Any extra keys beyond 'mode' and 'value' are not covered by the spec.
        extra_keys = set(payload.keys()) - {"mode", "value"}
        if extra_keys:
            raise NotImplementedError(
                f"Unspecified behaviour for 'echo' mode with extra keys: {extra_keys!r}"
            )
        return payload["value"]

    raise NotImplementedError(
        f"Unspecified behaviour for payload: {payload!r}"
    )
