def handle_underspecified(payload: dict) -> object:
    """
    Handle underspecified payloads.

    Specified behaviour:
        payload == {'mode': 'echo', 'value': X}   ->  return X
        payload == {'mode': 'count', 'items': L}  ->  return len(L)  (L must be a list)

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
        extra_keys = set(payload.keys()) - {"mode", "value"}
        if extra_keys:
            raise NotImplementedError(
                f"Unspecified behaviour for 'echo' mode with extra keys: {extra_keys!r}"
            )
        return payload["value"]

    if mode == "count":
        if "items" not in payload:
            raise NotImplementedError(
                "Unspecified behaviour for 'count' mode without 'items' key."
            )
        extra_keys = set(payload.keys()) - {"mode", "items"}
        if extra_keys:
            raise NotImplementedError(
                f"Unspecified behaviour for 'count' mode with extra keys: {extra_keys!r}"
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise NotImplementedError(
                f"Unspecified behaviour for 'count' mode with non-list items: {items!r}"
            )
        return len(items)

    raise NotImplementedError(
        f"Unspecified behaviour for payload: {payload!r}"
    )
