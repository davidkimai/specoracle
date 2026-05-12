"""
A module for handling underspecified payloads based on a strict specification.
"""

from typing import Any, Dict


def handle_underspecified(payload: Dict[str, Any]) -> Any:
    """
    Processes a payload dictionary according to a narrow specification.

    The only specified behavior is for a payload of the exact form:
    {'mode': 'echo', 'value': X}
    In this case, the function returns X.

    For any other input, including payloads with extra keys, missing keys,
    or different modes, this function raises a NotImplementedError, as the
    behavior for such cases is undefined.

    Args:
        payload: The input dictionary to process. The type hint is broad,
                 but the implementation is strict.

    Returns:
        The value associated with the 'value' key if the payload matches
        the specified 'echo' mode structure.

    Raises:
        NotImplementedError: For any payload that does not strictly match
                             the specified structure and mode.
    """
    # The specification is for a dictionary with exactly two keys: 'mode' and 'value'.
    # The 'mode' must be 'echo'.
    # We check all conditions in a single expression for simplicity.
    if (
        isinstance(payload, dict)
        and len(payload) == 2
        and payload.get("mode") == "echo"
        and "value" in payload
    ):
        return payload["value"]
    else:
        # Any deviation from the single specified path is an uncovered case.
        raise NotImplementedError("Unspecified payload structure or mode")
