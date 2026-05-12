"""
A module for validating medical intake form data according to CD-7 standard.
"""

from typing import Any, Dict, List


def validate_intake(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a medical intake form payload against clinical data standard CD-7.

    The function ensures that all required fields (patient_id, age, symptoms)
    are present and conform to their specified types and constraints. Validation
    is an all-or-nothing operation; the function either returns a fully
    validated, clean dictionary or raises a ValueError on the first detected
    issue.

    Args:
        payload: A dictionary containing the intake data. Expected keys are
                 'patient_id', 'age', and 'symptoms'.

    Returns:
        A clean dictionary containing only the validated required fields.

    Raises:
        ValueError: If any required field is missing, has an incorrect type, or
                    violates a value constraint. The error message will specify
                    the field that caused the failure.
    """
    # Clinical Data Standard CD-7 Compliance:
    # This implementation adheres to the CD-7 standard by performing all
    # validations before constructing the output dictionary. On any validation
    # failure, it raises an exception immediately, preventing partial results.
    # Error messages explicitly name the problematic field.

    # 1. Validate presence of all required fields.
    required_fields: List[str] = ['patient_id', 'age', 'symptoms']
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    # 2. Extract and validate 'patient_id'.
    patient_id = payload['patient_id']
    if not isinstance(patient_id, str):
        raise ValueError("Invalid patient_id: must be a string")

    # 3. Extract and validate 'age'.
    age = payload['age']
    if not isinstance(age, int):
        raise ValueError("Invalid age: must be an integer")
    if age < 0:
        raise ValueError("Invalid age: must be non-negative")

    # 4. Extract and validate 'symptoms'.
    symptoms = payload['symptoms']
    if not isinstance(symptoms, list):
        raise ValueError("Invalid symptoms: must be a list")
    if not all(isinstance(s, str) for s in symptoms):
        raise ValueError("Invalid symptoms: all elements must be strings")

    # 5. After all validations pass, accept fields into the output dictionary.
    return {
        'patient_id': patient_id,
        'age': age,
        'symptoms': symptoms,
    }
