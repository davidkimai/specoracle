"""
Module for validating medical intake form data.
"""

import typing

def validate_intake(payload: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """
    Validates a medical intake payload.

    The payload must contain 'patient_id', 'age', and 'symptoms'.
    - 'patient_id' must be a non-empty string.
    - 'age' must be an integer greater than or equal to 0.
    - 'symptoms' must be a list of strings.

    Args:
        payload: A dictionary representing the intake form data.

    Returns:
        A new dictionary containing the validated 'patient_id', 'age',
        and 'symptoms' if the payload is valid.

    Raises:
        ValueError: If a required field is missing, has an incorrect type,
                    or an invalid value. The error message will contain the
                    name of the invalid field.
    """
    # Validate 'patient_id'
    patient_id = payload.get('patient_id')
    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("patient_id")

    # Validate 'age'
    age = payload.get('age')
    # Use `type(age) is not int` to avoid booleans being treated as ints
    if type(age) is not int or age < 0:
        raise ValueError("age")

    # Validate 'symptoms'
    symptoms = payload.get('symptoms')
    if not isinstance(symptoms, list) or not all(isinstance(s, str) for s in symptoms):
        raise ValueError("symptoms")

    # Return a clean dictionary with only the validated fields
    clean_data = {
        'patient_id': patient_id.strip(),
        'age': age,
        'symptoms': symptoms,
    }

    return clean_data
