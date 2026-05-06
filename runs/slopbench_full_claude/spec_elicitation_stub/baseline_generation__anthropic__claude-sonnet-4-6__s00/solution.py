"""
Module: spec_elicitation_stub

Provides handle_underspecified(payload: dict) -> object.

Specified behaviour:
    payload == {'mode': 'echo', 'value': X}  ->  returns X

All other inputs raise NotImplementedError, signalling that the behaviour for
those paths has not yet been specified and must be elicited from stakeholders
before implementation.
"""


def handle_underspecified(payload: dict) -> object:
    """
    Handle a payload dict according to the currently specified paths.

    Parameters
    ----------
    payload : dict
        The input mapping describing the requested operation.

    Returns
    -------
    object
        The result of the specified operation.

    Raises
    ------
    TypeError
        If *payload* is not a dict.
    NotImplementedError
        For any input path that has not yet been specified.
    """
    if not isinstance(payload, dict):
        raise TypeError(
            f"payload must be a dict, got {type(payload).__name__!r}"
        )

    mode = payload.get("mode")

    if mode == "echo":
        if "value" not in payload:
            raise NotImplementedError(
                "The 'echo' mode requires a 'value' key; "
                "behaviour when 'value' is absent is not specified."
            )
        return payload["value"]

    raise NotImplementedError(
        f"No behaviour is specified for payload {payload!r}. "
        "Please elicit requirements for this input path before implementing."
    )
