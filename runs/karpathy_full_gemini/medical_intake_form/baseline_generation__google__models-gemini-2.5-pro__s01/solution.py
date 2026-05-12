"""
Module for validating medical intake form data.

This module provides a function to validate and clean a dictionary
representing a patient's medical intake form, ensuring all required
fields are present and correctly formatted.
"""

from typing import Any, Dict, List

__all__ = ['validate_intake']


def validate_intake(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and cleans a medical intake form payload.

    The function checks for the presence, type, and validity of required
    fields: 'patient_id', 'age', and 'symptoms'. If validation is
    successful, it returns a new dictionary containing only these
    validated fields. Any leading/trailing whitespace in string fields
    is removed.

    Args:
        payload: A dictionary containing the intake form data.

    Returns:
        A new dictionary with the validated 'patient_id', 'age', and
        'symptoms' fields.

    Raises:
        ValueError: If any field is missing, has an incorrect type, or
                    contains an invalid value. The error message will
                    name the problematic field.
    """
    clean_data: Dict[str, Any] = {}

    # 1. Validate 'patient_id'
    if 'patient_id' not in payload:
        raise ValueError("Missing required field: patient_id")

    patient_id = payload['patient_id']
    if not isinstance(patient_id, str):
        raise ValueError("Field 'patient_id' must be a string.")

    patient_id_stripped = patient_id.strip()
    if not patient_id_stripped:
        raise ValueError("Field 'patient_id' cannot be empty.")

    clean_data['patient_id'] = patient_id_stripped

    # 2. Validate 'age'
    if 'age' not in payload:
        raise ValueError("Missing required field: age")

    age = payload['age']
    # The check `isinstance(age, bool)` is necessary because in Python,
    # `isinstance(True, int)` evaluates to True.
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("Field 'age' must be an integer.")

    if age < 0:
        raise ValueError("Field 'age' must be a non-negative integer.")

    clean_data['age'] = age

    # 3. Validate 'symptoms'
    if 'symptoms' not in payload:
        raise ValueError("Missing required field: symptoms")

    symptoms = payload['symptoms']
    if not isinstance(symptoms, list):
        raise ValueError("Field 'symptoms' must be a list.")

    clean_symptoms: List[str] = []
    for item in symptoms:
        if not isinstance(item, str):
            raise ValueError("All items in 'symptoms' list must be strings.")
        symptom_stripped = item.strip()
        if not symptom_stripped:
            raise ValueError("Symptom strings in 'symptoms' list cannot be empty.")
        clean_symptoms.append(symptom_stripped)

    clean_data['symptoms'] = clean_symptoms

    return clean_data
