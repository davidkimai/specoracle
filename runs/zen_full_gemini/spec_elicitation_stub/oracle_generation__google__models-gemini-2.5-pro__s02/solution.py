"""
A module for handling underspecified payloads based on a dispatch key.

This module provides a function to process dictionary payloads where the
behavior is determined by a 'mode' key. It is designed to be strict,
only handling explicitly specified paths and rejecting all others.
"""

from typing import Any, Dict


def handle_underspecified(payload: Dict[str, Any]) -> Any:
    """
    Processes a payload dictionary based on a 'mode' key.

    The only currently specified behavior is for 'echo' mode, which returns
    the associated 'value'. All other inputs are considered underspecified
    and will result in an error.

    Args:
        payload: The input dictionary to process.

    Returns:
        The value associated with the 'value' key if mode is 'echo'.

    Raises:
        NotImplementedError: If the payload is not a dictionary, if the mode
                             is not 'echo', or if the 'value' key is missing
                             in 'echo' mode.
    """
    if not isinstance(payload, dict):
        raise NotImplementedError("Payload must be a dictionary.")

    mode = payload.get("mode")
    if mode != "echo":
        # Provide a clear error message for the unsupported mode.
        # The !r ensures the representation is developer-friendly (e.g., shows quotes).
        raise NotImplementedError(
            f"Unsupported mode: {mode!r}. Only 'echo' is implemented."
        )

    if "value" not in payload:
        raise NotImplementedError("Missing 'value' key for 'echo' mode.")

    return payload["value"]
