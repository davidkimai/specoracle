"""
medical_intake_form.py

Provides validate_intake(payload: dict) -> dict for validating and cleaning
medical intake form submissions.
"""

from __future__ import annotations


def validate_intake(payload: dict) -> dict:
    """Validate a medical intake form payload.

    Required fields
    ---------------
    patient_id : str
        Non-empty string identifier for the patient.
    age : int
        Integer >= 0 representing the patient's age.
    symptoms : list[str]
        A list (possibly empty) of symptom strings; every element must be a str.

    Parameters
    ----------
    payload : dict
        Raw input dictionary to validate.

    Returns
    -------
    dict
        A clean dictionary containing only the validated fields with their
        normalised types.

    Raises
    ------
    ValueError
        Raised with a message that names the offending field when any
        validation rule is violated.
    TypeError
        Raised when *payload* itself is not a dict.
    """
    if not isinstance(payload, dict):
        raise TypeError(
            f"payload must be a dict, got {type(payload).__name__!r}"
        )

    # ------------------------------------------------------------------ #
    # patient_id
    # ------------------------------------------------------------------ #
    if "patient_id" not in payload:
        raise ValueError("patient_id: field is required")

    patient_id = payload["patient_id"]

    if not isinstance(patient_id, str):
        raise ValueError(
            f"patient_id: expected str, got {type(patient_id).__name__!r}"
        )

    patient_id = patient_id.strip()

    if not patient_id:
        raise ValueError("patient_id: must not be an empty or blank string")

    # ------------------------------------------------------------------ #
    # age
    # ------------------------------------------------------------------ #
    if "age" not in payload:
        raise ValueError("age: field is required")

    age = payload["age"]

    # Accept only int; explicitly reject bool because bool is a subclass of
    # int in Python but semantically wrong here.
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError(
            f"age: expected int, got {type(age).__name__!r}"
        )

    if age < 0:
        raise ValueError(f"age: must be >= 0, got {age!r}")

    # ------------------------------------------------------------------ #
    # symptoms
    # ------------------------------------------------------------------ #
    if "symptoms" not in payload:
        raise ValueError("symptoms: field is required")

    symptoms = payload["symptoms"]

    if not isinstance(symptoms, list):
        raise ValueError(
            f"symptoms: expected list, got {type(symptoms).__name__!r}"
        )

    cleaned_symptoms: list[str] = []
    for index, item in enumerate(symptoms):
        if not isinstance(item, str):
            raise ValueError(
                f"symptoms: element at index {index} must be str, "
                f"got {type(item).__name__!r}"
            )
        cleaned_symptoms.append(item)

    # ------------------------------------------------------------------ #
    # Return clean payload
    # ------------------------------------------------------------------ #
    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": cleaned_symptoms,
    }
