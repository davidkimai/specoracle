"""
A module for validating medical intake form data according to clinical standards.
"""

from typing import Dict, Any, List

def validate_intake(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a medical intake payload against required fields and constraints.

    This function adheres to Clinical Data Standard CD-7:
    - It validates every required field before accepting any field into the output.
    - Error messages name the specific field that failed validation.
    - Partial validation is not permitted; the function returns a complete,
      validated dictionary only after all required fields have passed all checks.

    Args:
        payload: A dictionary containing the intake data. Expected keys are
                 'patient_id', 'age', and 'symptoms'.

    Returns:
        A dictionary containing the clean, validated data for the required fields.

    Raises:
        ValueError: If any required field is missing, has an incorrect type,
                    or violates a value constraint.
    """
    required_fields: set[str] = {"patient_id", "age", "symptoms"}

    # --- Pre-validation Step: Check for presence of all required fields ---
    # This check must pass completely before proceeding to type/value validation.
    for field_name in required_fields:
        if field_name not in payload:
            raise ValueError(f"Missing required field: {field_name}")

    # --- Field-by-field Validation ---
    # Each field is checked for type and value constraints. A failure at any
    # point will raise an exception immediately, preventing the creation of a
    # partially validated output.

    # Validate 'patient_id'
    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("Invalid patient_id: must be a string.")
    if not patient_id.strip():
        raise ValueError("Invalid patient_id: cannot be empty or just whitespace.")

    # Validate 'age'
    age = payload["age"]
    # Note: `isinstance(True, int)` is True, so we must explicitly block bools.
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("Invalid age: must be an integer.")
    if age < 0:
        raise ValueError("Invalid age: must be non-negative.")

    # Validate 'symptoms'
    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("Invalid symptoms: must be a list.")
    if not all(isinstance(s, str) for s in symptoms):
        raise ValueError("Invalid symptoms: all items in the list must be strings.")

    # --- Success ---
    # All validations passed. The function can now return the clean output dict.
    return {
        "patient_id": patient_id.strip(),
        "age": age,
        "symptoms": symptoms,
    }
