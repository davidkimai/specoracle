from typing import Any


def handle_underspecified(payload: dict) -> object:
    """
    Handle the single specified input path.

    Specified behavior:
        {'mode': 'echo', 'value': X} -> X

    All other inputs are intentionally unsupported.
    """
    if (
        isinstance(payload, dict)
        and set(payload.keys()) == {"mode", "value"}
        and payload.get("mode") == "echo"
    ):
        return payload["value"]

    raise NotImplementedError("Behavior is only specified for {'mode': 'echo', 'value': X}.")
