"""
spec_elicitation_stub.py

Implements handle_underspecified according to the specified contract.
Only the {'mode': 'echo', 'value': X} path is defined; all other inputs
raise NotImplementedError to make gaps in the specification explicit.
"""


def handle_underspecified(payload: dict) -> object:
    """
    Handle a payload according to its 'mode'.

    Specified behaviour:
        {'mode': 'echo', 'value': X}  ->  returns X

    All other inputs raise NotImplementedError.
    """
    if not isinstance(payload, dict):
        raise TypeError(f"payload must be a dict, got {type(payload).__name__!r}")

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise KeyError("echo mode requires a 'value' key in payload")
        return payload["value"]

    raise NotImplementedError(
        f"No behaviour is specified for payload with mode={mode!r}. "
        "Extend the specification before adding an implementation."
    )
