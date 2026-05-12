"""
A module for validating medical intake form data based on CD-7 standards.
"""

import typing

__all__ = ['validate_intake']

_REQUIRED_FIELDS = frozenset({'patient_id', 'age', 'symptoms'})


def validate_intake(payload: dict[str, typing.Any]) -> dict[str, typing.Any]:
    """
    Validates a medical intake payload against required fields and rules.

    This function adheres to the Clinical Data Standard CD-7, ensuring that all
    required fields are present and valid before returning a clean data
    dictionary. If any validation fails, it raises a ValueError, preventing
    the processing of partial or invalid data.

    Args:
        payload: A dictionary containing the intake data. Expected keys are
                 'patient_id', 'age', and 'symptoms'.

    Returns:
        A new dictionary containing only the validated required fields.

    Raises:
        ValueError: If a required field is missing, has an incorrect type, or
                    violates a value constraint. The error message will
                    specify the field that caused the failure.
    """
    # CD-7: Validate every required field before accepting any field.
    # The following checks are performed sequentially. A failure at any point
    # will raise an exception, preventing the function from returning a
    # partially validated or incomplete result.

    # 1. Check for the presence of all required fields.
    missing_fields = _REQUIRED_FIELDS - payload.keys()
    if missing_fields:
        # Report the first missing field alphabetically for deterministic errors.
        field_name = sorted(list(missing_fields))[0]
        raise ValueError(f"Missing required field: '{field_name}'")

    # 2. Extract and validate 'patient_id'.
    patient_id = payload['patient_id']
    if not isinstance(patient_id, str):
        raise ValueError("Field 'patient_id' must be a string.")

    # 3. Extract and validate 'age'.
    age = payload['age']
    # Note: `isinstance(True, int)` is True, so we must explicitly reject bools.
    if not isinstance(age, int) or isinstance(age, bool):
        raise ValueError("Field 'age' must be an integer.")
    if age < 0:
        raise ValueError("Field 'age' must be a non-negative integer.")

    # 4. Extract and validate 'symptoms'.
    symptoms = payload['symptoms']
    if not isinstance(symptoms, list):
        raise ValueError("Field 'symptoms' must be a list.")
    if not all(isinstance(item, str) for item in symptoms):
        raise ValueError("All items in 'symptoms' must be strings.")

    # CD-7: Return only after all required fields pass validation.
    # If execution reaches this point, all validations have succeeded.
    return {
        'patient_id': patient_id,
        'age': age,
        'symptoms': symptoms,
    }
