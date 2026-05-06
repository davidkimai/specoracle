def handle_underspecified(payload: dict) -> object:
    """
    Handle underspecified payloads.

    Fully specified behaviours:
        payload == {'mode': 'echo', 'value': X}          ->  return X
        payload == {'mode': 'count', 'items': <list>}    ->  return len(items)

    Every other input path raises NotImplementedError so that callers are
    forced to extend this function with explicit, reviewed behaviour rather
    than relying on silent guesses.
    """
    if not isinstance(payload, dict):
        raise NotImplementedError(
            "Behaviour for non-dict payloads is not specified."
        )

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise NotImplementedError(
                "Behaviour for 'echo' mode without a 'value' key is not specified."
            )
        # Reject unexpected extra keys so that callers cannot accidentally
        # rely on undocumented behaviour hidden inside a nominally-echo payload.
        extra_keys = payload.keys() - {"mode", "value"}
        if extra_keys:
            raise NotImplementedError(
                f"Behaviour for 'echo' mode with extra keys {extra_keys!r} "
                "is not specified."
            )
        return payload["value"]

    if mode == "count":
        if "items" not in payload:
            raise NotImplementedError(
                "Behaviour for 'count' mode without an 'items' key is not specified."
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise NotImplementedError(
                "Behaviour for 'count' mode where 'items' is not a list is not specified."
            )
        extra_keys = payload.keys() - {"mode", "items"}
        if extra_keys:
            raise NotImplementedError(
                f"Behaviour for 'count' mode with extra keys {extra_keys!r} "
                "is not specified."
            )
        return len(items)

    raise NotImplementedError(
        f"Behaviour for mode={mode!r} is not specified."
    )
