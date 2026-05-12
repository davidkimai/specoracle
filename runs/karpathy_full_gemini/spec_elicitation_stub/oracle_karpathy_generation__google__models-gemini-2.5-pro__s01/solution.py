"""
A module to handle underspecified payloads based on explicit requirements.
"""

from typing import Any, Dict


def handle_underspecified(payload: Dict[str, Any]) -> Any:
    """
    Processes a payload according to a narrow specification.

    The only specified behavior is for a payload of the exact form:
    {'mode': 'echo', 'value': X}
    which should return X.

    For any other input, this function raises a NotImplementedError, as the
    behavior for other cases is undefined.

    Args:
        payload: The input dictionary to process.

    Returns:
        The value associated with the 'value' key if the payload matches the
        'echo' mode specification.

    Raises:
        NotImplementedError: If the payload does not strictly match the
                             specified format.
    """
    if (
        isinstance(payload, dict)
        and len(payload) == 2
        and payload.get("mode") == "echo"
        and "value" in payload
    ):
        return payload["value"]
    else:
        raise NotImplementedError("Behavior for this payload is not specified.")
