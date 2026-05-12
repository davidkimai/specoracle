"""
Module for validating medical intake form data.

This module provides functionality to validate a patient's intake data
according to the Clinical Data Standard CD-7.
"""

from typing import Any, Dict, List


def validate_intake(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a medical intake payload.

    According to Clinical Data Standard CD-7, this function validates that
    all required fields (`patient_id`, `age`, `symptoms`) are present and
    correctly typed. Validation is all-or-nothing; a complete, clean
    dictionary is returned on success, or a ValueError is raised on the
    first validation failure.

    Args:
        payload: A dictionary containing the intake data.

    Returns:
        A new dictionary containing only the validated required fields.

    Raises:
        ValueError: If any validation fails. The error message will
                    specify the field and the reason for failure.
    """
    required_fields = ['patient_id', 'age', 'symptoms']
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    # Extract and validate patient_id
    patient_id = payload['patient_id']
    if not isinstance(patient_id, str):
        raise ValueError("Field 'patient_id' must be a string.")

    # Extract and validate age
    age = payload['age']
    # `bool` is a subclass of `int`, so `isinstance(True, int)` is True.
    # We must use `type()` to explicitly reject booleans.
    if type(age) is not int:
        raise ValueError("Field 'age' must be an integer.")
    if age < 0:
        raise ValueError("Field 'age' must be a non-negative integer.")

    # Extract and validate symptoms
    symptoms = payload['symptoms']
    if not isinstance(symptoms, list):
        raise ValueError("Field 'symptoms' must be a list.")
    if not all(isinstance(s, str) for s in symptoms):
        raise ValueError("All items in 'symptoms' must be strings.")

    # Per CD-7, return clean data only after all validations pass.
    return {
        'patient_id': patient_id,
        'age': age,
        'symptoms': symptoms,
    }
