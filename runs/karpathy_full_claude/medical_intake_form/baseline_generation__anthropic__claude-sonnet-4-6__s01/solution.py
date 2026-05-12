"""
medical_intake_form.py

Provides validate_intake(payload: dict) -> dict for validating and cleaning
medical intake form data.
"""

from __future__ import annotations


def validate_intake(payload: dict) -> dict:
    """Validate a medical intake form payload.

    Required fields
    ---------------
    patient_id : str
        Non-empty string identifying the patient.
    age : int
        Integer >= 0.
    symptoms : list[str]
        List of symptom strings (may be empty, but must be a list).

    Returns
    -------
    dict
        A clean copy of the validated payload containing exactly the three
        required fields with their canonical types.

    Raises
    ------
    ValueError
        If any required field is missing or fails type/value validation.
        The exception message names the offending field.
    TypeError
        If *payload* itself is not a dict.
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

    # --- patient_id ---
    if "patient_id" not in payload:
        raise ValueError("patient_id")
    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("patient_id")
    if not patient_id.strip():
        raise ValueError("patient_id")

    # --- age ---
    if "age" not in payload:
        raise ValueError("age")
    age = payload["age"]
    # Reject booleans (bool is a subclass of int in Python)
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("age")
    if age < 0:
        raise ValueError("age")

    # --- symptoms ---
    if "symptoms" not in payload:
        raise ValueError("symptoms")
    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("symptoms")
    for item in symptoms:
        if not isinstance(item, str):
            raise ValueError("symptoms")

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
