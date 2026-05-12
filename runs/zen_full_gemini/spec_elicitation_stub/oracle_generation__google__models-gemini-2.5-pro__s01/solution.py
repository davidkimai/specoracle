"""
A module for handling underspecified payloads based on a strict specification.
"""

def handle_underspecified(payload: dict) -> object:
    """
    Processes a payload according to a limited, explicit specification.

    The only specified behavior is for a payload of the form:
    {'mode': 'echo', 'value': X}
    which results in the function returning X.

    For any other input, this function raises a NotImplementedError,
    refusing to guess the intended behavior for unspecified cases.

    Args:
        payload: The input dictionary to process.

    Returns:
        The value associated with the 'value' key if the payload matches
        the 'echo' mode specification.

    Raises:
        NotImplementedError: If the payload does not conform to the
                             specified structure and values.
    """
    if not isinstance(payload, dict):
        # This check handles cases where non-dict types are passed,
        # ensuring robustness beyond static type hints.
        raise NotImplementedError("Input payload must be a dictionary.")

    mode = payload.get("mode")
    if mode != "echo":
        # This clause covers both a missing 'mode' key (where .get() returns None)
        # and a 'mode' key with an unsupported value.
        raise NotImplementedError(f"Unsupported or missing mode: received '{mode}'.")

    if "value" not in payload:
        # The 'echo' mode specification explicitly requires a 'value' key.
        raise NotImplementedError("Payload for 'echo' mode must include a 'value' key.")

    return payload["value"]
