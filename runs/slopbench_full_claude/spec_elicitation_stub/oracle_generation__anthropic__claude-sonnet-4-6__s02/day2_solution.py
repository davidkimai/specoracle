"""
spec_elicitation_stub.py

Implements handle_underspecified according to the specified contract.

Specified behaviour:
    {'mode': 'echo',  'value': X}     ->  returns X
    {'mode': 'count', 'items': list}  ->  returns len(items)

All other inputs raise NotImplementedError to make gaps in the specification explicit.
"""


def handle_underspecified(payload: dict) -> object:
    """
    Handle a payload according to its 'mode'.

    Specified behaviour:
        {'mode': 'echo',  'value': X}     ->  returns X
        {'mode': 'count', 'items': list}  ->  returns len(items)

    All other inputs raise NotImplementedError.
    """
    if not isinstance(payload, dict):
        raise TypeError(f"payload must be a dict, got {type(payload).__name__!r}")

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise KeyError("echo mode requires a 'value' key in payload")
        return payload["value"]

    if mode == "count":
        if "items" not in payload:
            raise KeyError("count mode requires an 'items' key in payload")
        items = payload["items"]
        if not isinstance(items, list):
            raise TypeError(
                f"count mode requires 'items' to be a list, got {type(items).__name__!r}"
            )
        return len(items)

    raise NotImplementedError(
        f"No behaviour is specified for payload with mode={mode!r}. "
        "Extend the specification before adding an implementation."
    )
