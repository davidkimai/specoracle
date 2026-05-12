"""
A module for validating medical intake form data.

This module provides a function to validate and clean a dictionary representing
a patient's medical intake form, ensuring all required fields are present and
adhere to specified constraints.
"""

import typing


def validate_intake(payload: dict) -> dict:
    """
    Validates and cleans a medical intake form payload.

    The payload must be a dictionary and contain the following fields:
    - 'patient_id': A non-empty string.
    - 'age': A non-negative integer.
    - 'symptoms': A list where every element is a string.

    The function performs the following checks:
    1.  Ensures all required fields are present.
    2.  Verifies the data type of each field.
    3.  Validates the value of each field against its specific constraints
        (e.g., age must be non-negative).

    If validation is successful, it returns a new dictionary containing the
    cleaned data. String fields are stripped of leading/trailing whitespace.

    Args:
        payload: A dictionary representing the intake form data.

    Returns:
        A new dictionary containing the cleaned and validated data.

    Raises:
        TypeError: If the provided payload is not a dictionary.
        ValueError: If any field is missing, has an incorrect type, or contains
                    an invalid value. The error message will specify the
                    problematic field and the nature of the error.
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary.")

    required_fields = {
        'patient_id': str,
        'age': int,
        'symptoms': list,
    }

    clean_data = {}

    # 1. Check for presence and correct base types of required fields.
    for field, expected_type in required_fields.items():
        if field not in payload:
            raise ValueError(f"Missing required field: '{field}'")

        value = payload[field]

        # In Python, bool is a subclass of int, but for an 'age' field,
        # a boolean value is typically not desired. We explicitly check for it.
        if expected_type is int and isinstance(value, bool):
            raise ValueError(
                f"Invalid type for field '{field}': "
                f"expected {expected_type.__name__}, got bool"
            )

        if not isinstance(value, expected_type):
            raise ValueError(
                f"Invalid type for field '{field}': "
                f"expected {expected_type.__name__}, got {type(value).__name__}"
            )
        
        clean_data[field] = value

    # 2. Perform value-specific validations and cleaning.

    # Validate and clean 'patient_id'
    patient_id = clean_data['patient_id']
    if not patient_id.strip():
        raise ValueError("Invalid value for field 'patient_id': cannot be empty")
    clean_data['patient_id'] = patient_id.strip()

    # Validate 'age'
    age = clean_data['age']
    if age < 0:
        raise ValueError("Invalid value for field 'age': must be non-negative")

    # Validate 'symptoms'
    symptoms = clean_data['symptoms']
    if not all(isinstance(s, str) for s in symptoms):
        raise ValueError(
            "Invalid value for field 'symptoms': all items must be strings"
        )
    
    # Clean up symptoms: strip whitespace and remove empty strings.
    clean_data['symptoms'] = [s.strip() for s in symptoms if s.strip()]

    return clean_data
