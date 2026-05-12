"""
This module provides a handler for a partially specified task.
"""

import typing


def handle_underspecified(payload: dict) -> object:
    """
    Handles a payload according to a limited specification.

    The only specified behavior is for a payload of the exact form:
    {'mode': 'echo', 'value': X}
    which results in the function returning X.

    For any other input, this function raises a NotImplementedError to avoid
    any unintended or insecure behavior. This "fail-safe" approach prevents
    guessing at unspecified functionality.

    Args:
        payload: The input dictionary to process.

    Returns:
        The value associated with the 'value' key if the payload matches
        the specified 'echo' mode structure.

    Raises:
        NotImplementedError: If the payload does not match the strictly
                             defined specification.
    """
    # 1. Validate the type of the payload.
    #    The specification is only defined for dictionaries.
    if not isinstance(payload, dict):
        raise NotImplementedError("Unsupported payload: input must be a dictionary.")

    # 2. Validate the structure and content of the dictionary.
    #    The specification is for a dictionary with exactly two keys,
    #    'mode' and 'value', where 'mode' has the value 'echo'.
    #    This strict check prevents processing of payloads with unexpected
    #    or extra keys.
    if payload.keys() == {'mode', 'value'} and payload['mode'] == 'echo':
        # This is the only valid, specified path.
        return payload['value']

    # 3. For all other inputs, the behavior is undefined.
    #    The safe and correct action is to refuse to proceed.
    raise NotImplementedError("Unsupported payload: unknown mode or format.")
