"""
spec_elicitation_stub.py

Implements handle_underspecified according to the specification:
  - payload {'mode': 'echo', 'value': X} -> returns X
  - all other inputs -> raises NotImplementedError
"""


def handle_underspecified(payload: dict) -> object:
    """
    Handle an underspecified payload.

    Specified behaviour:
        payload == {'mode': 'echo', 'value': X}  ->  return X

    All other inputs raise NotImplementedError to signal that the behaviour
    for those paths has not yet been specified.

    Parameters
    ----------
    payload : dict
        The input mapping to dispatch on.

    Returns
    -------
    object
        The value associated with the 'value' key when mode is 'echo'.

    Raises
    ------
    TypeError
        If *payload* is not a dict.
    NotImplementedError
        For every input path that is not explicitly specified.
    """
    if not isinstance(payload, dict):
        raise TypeError(f"payload must be a dict, got {type(payload).__name__!r}")

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise NotImplementedError(
                "mode 'echo' requires a 'value' key, but none was provided; "
                "behaviour for this case is not specified."
            )
        return payload["value"]

    raise NotImplementedError(
        f"No specified behaviour for payload with mode={mode!r}. "
        "Only mode='echo' is currently specified."
    )
