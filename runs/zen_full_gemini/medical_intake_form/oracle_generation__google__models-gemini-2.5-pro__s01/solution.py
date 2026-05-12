# medical_intake_form.py
# This module provides functionality for validating medical intake forms.

import typing


def validate_intake(payload: dict) -> dict:
    """
    Validates a medical intake payload against required fields and types.

    According to the Clinical Data Standard CD-7, this function validates every
    required field before creating the output. Validation is atomic; if any
    check fails, an exception is raised and no data is returned.

    Args:
        payload: A dictionary containing the intake data. Expected keys are
                 'patient_id', 'age', and 'symptoms'.

    Returns:
        A new dictionary containing only the validated, required fields.

    Raises:
        ValueError: If a required field is missing, has an incorrect type,
                    or contains an invalid value. The error message will
                    specify the field that caused the failure.
    """
    # 1. Check for presence of all required fields. This must be done before
    #    accessing any values to comply with the all-or-nothing validation rule.
    required_fields = ("patient_id", "age", "symptoms")
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    # 2. Extract and validate 'patient_id'.
    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("Field 'patient_id' must be a string.")

    # 3. Extract and validate 'age'.
    age = payload["age"]
    # Use `type() is int` to reject booleans, as `isinstance(True, int)` is True.
    if type(age) is not int:
        raise ValueError("Field 'age' must be an integer.")
    if age < 0:
        raise ValueError("Field 'age' must be non-negative.")

    # 4. Extract and validate 'symptoms'.
    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("Field 'symptoms' must be a list.")
    if not all(isinstance(item, str) for item in symptoms):
        raise ValueError("Field 'symptoms' must be a list of strings.")

    # 5. If all validations pass, construct and return the clean data structure.
    # This fulfills the CD-7 requirement to only accept fields into the output
    # after all validations are successful.
    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": symptoms,
    }
