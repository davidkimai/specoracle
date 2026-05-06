"""
medical_intake_form.py

Provides validate_intake(payload: dict) -> dict for validating and cleaning
medical intake form submissions.
"""

from __future__ import annotations

from typing import Callable


def validate_intake(
    payload: dict,
    optional_fields: dict[str, Callable] | None = None,
) -> dict:
    """Validate a medical intake form payload.

    Required fields
    ---------------
    patient_id : str
        Non-empty string identifier for the patient.
    age : int
        Integer >= 0 representing the patient's age.
    symptoms : list[str]
        A list of symptom strings (may be empty, but must be a list).

    Parameters
    ----------
    payload : dict
        The raw intake form data.
    optional_fields : dict[str, callable] | None
        Mapping of optional field names to validator callables.  Each
        callable receives the raw field value and must return the cleaned
        value or raise an exception if the value is invalid.  Optional
        fields that are absent from *payload* are silently skipped.  If a
        validator raises any exception the field name is re-raised as a
        ``ValueError`` naming the offending field.

    Returns
    -------
    dict
        A cleaned dictionary containing the validated required fields plus
        any optional fields that were present and valid.

    Raises
    ------
    ValueError
        If any required field is missing or fails validation, or if a
        present optional field fails its validator.  The exception message
        names the offending field.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    cleaned: dict = {}

    # ------------------------------------------------------------------ #
    # patient_id
    # ------------------------------------------------------------------ #
    if "patient_id" not in payload:
        raise ValueError("patient_id")

    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("patient_id")
    patient_id = patient_id.strip()
    if not patient_id:
        raise ValueError("patient_id")
    cleaned["patient_id"] = patient_id

    # ------------------------------------------------------------------ #
    # age
    # ------------------------------------------------------------------ #
    if "age" not in payload:
        raise ValueError("age")

    age = payload["age"]
    # Booleans are a subclass of int in Python; reject them explicitly.
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("age")
    if age < 0:
        raise ValueError("age")
    cleaned["age"] = age

    # ------------------------------------------------------------------ #
    # symptoms
    # ------------------------------------------------------------------ #
    if "symptoms" not in payload:
        raise ValueError("symptoms")

    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("symptoms")
    cleaned_symptoms: list[str] = []
    for item in symptoms:
        if not isinstance(item, str):
            raise ValueError("symptoms")
        cleaned_symptoms.append(item)
    cleaned["symptoms"] = cleaned_symptoms

    # ------------------------------------------------------------------ #
    # optional fields
    # ------------------------------------------------------------------ #
    if optional_fields:
        for field_name, validator in optional_fields.items():
            if field_name not in payload:
                continue
            try:
                cleaned[field_name] = validator(payload[field_name])
            except Exception:
                raise ValueError(field_name)

    return cleaned
