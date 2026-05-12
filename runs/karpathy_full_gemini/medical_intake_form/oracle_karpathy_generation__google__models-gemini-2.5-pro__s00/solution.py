"""
A module for validating medical intake form data based on Clinical Data Standard CD-7.
"""

import typing

__all__ = ['validate_intake']


def validate_intake(payload: dict) -> dict:
    """
    Validates a medical intake payload against required fields and constraints.

    The validation follows the "all-or-nothing" principle specified by
    Clinical Data Standard CD-7. All required fields must be present and
    valid before a result is returned. If any validation fails, an exception
    is raised immediately.

    Required fields:
    - patient_id (str): The unique identifier for the patient.
    - age (int): The patient's age, must be non-negative.
    - symptoms (list[str]): A list of symptoms described by the patient.

    Args:
        payload: A dictionary representing the raw intake data.

    Returns:
        A clean dictionary containing only the validated required fields.

    Raises:
        ValueError: If a required field is missing, has an incorrect type,
                    or violates a value constraint. The error message will
                    name the field that caused the failure.
    """
    # Per CD-7, validate every required field before accepting any field.
    # We begin by checking for the presence of all required keys.
    required_fields = ['patient_id', 'age', 'symptoms']
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field '{field}'.")

    # Extract values now that presence is confirmed.
    patient_id = payload['patient_id']
    age = payload['age']
    symptoms = payload['symptoms']

    # Proceed with type and value validation for each field.
    # An error in any field will halt execution and prevent returning a
    # partially validated object.

    # Validate 'patient_id'
    if not isinstance(patient_id, str):
        raise ValueError("Invalid field 'patient_id': must be a string.")

    # Validate 'age'
    if not isinstance(age, int):
        raise ValueError("Invalid field 'age': must be an integer.")
    if age < 0:
        raise ValueError("Invalid field 'age': must be a non-negative integer.")

    # Validate 'symptoms'
    if not isinstance(symptoms, list):
        raise ValueError("Invalid field 'symptoms': must be a list.")
    if not all(isinstance(s, str) for s in symptoms):
        raise ValueError("Invalid field 'symptoms': must be a list of strings.")

    # If all validations pass, construct and return the clean output dictionary.
    # This fulfills the CD-7 requirement to only return after all fields pass.
    return {
        'patient_id': patient_id,
        'age': age,
        'symptoms': symptoms,
    }
