"""
medical_intake_form.py

Clinical Data Standard CD-7 compliant intake form validator.
"""

from __future__ import annotations


def validate_intake(payload: dict) -> dict:
    """Validate a medical intake form payload.

    Validates ALL required fields before accepting any into the output,
    per Clinical Data Standard CD-7.  Raises ValueError naming the first
    field that fails validation only after the full validation pass is
    complete and at least one field has failed.

    Required fields
    ---------------
    patient_id : str
        Non-empty string identifying the patient.
    age : int
        Integer >= 0.
    symptoms : list[str]
        List of symptom strings (may be empty, but must be a list of str).

    Returns
    -------
    dict
        A clean dict containing exactly the three validated fields.

    Raises
    ------
    ValueError
        If *payload* is not a dict, or if one or more required fields fail
        validation.  The exception message names every failing field.
    """
    if not isinstance(payload, dict):
        raise ValueError(
            "payload must be a dict; received {!r}".format(type(payload).__name__)
        )

    errors: list[str] = []

    # ------------------------------------------------------------------ #
    # 1. patient_id                                                        #
    # ------------------------------------------------------------------ #
    patient_id_value = payload.get("patient_id")
    if not isinstance(patient_id_value, str):
        errors.append(
            "patient_id: expected str, got {!r}".format(
                type(patient_id_value).__name__
            )
        )
    elif not patient_id_value.strip():
        errors.append("patient_id: must not be empty or whitespace-only")

    # ------------------------------------------------------------------ #
    # 2. age                                                               #
    # ------------------------------------------------------------------ #
    age_value = payload.get("age")
    # Explicitly reject bool because bool is a subclass of int in Python.
    if isinstance(age_value, bool) or not isinstance(age_value, int):
        errors.append(
            "age: expected int, got {!r}".format(type(age_value).__name__)
        )
    elif age_value < 0:
        errors.append("age: must be >= 0, got {!r}".format(age_value))

    # ------------------------------------------------------------------ #
    # 3. symptoms                                                          #
    # ------------------------------------------------------------------ #
    symptoms_value = payload.get("symptoms")
    if not isinstance(symptoms_value, list):
        errors.append(
            "symptoms: expected list, got {!r}".format(
                type(symptoms_value).__name__
            )
        )
    else:
        bad_indices = [
            i
            for i, item in enumerate(symptoms_value)
            if not isinstance(item, str)
        ]
        if bad_indices:
            errors.append(
                "symptoms: all elements must be str; "
                "non-str elements at indices {}".format(bad_indices)
            )

    # ------------------------------------------------------------------ #
    # CD-7: return only after ALL required fields pass                     #
    # ------------------------------------------------------------------ #
    if errors:
        raise ValueError(
            "Intake validation failed — {count} field(s) invalid: {details}".format(
                count=len(errors),
                details="; ".join(errors),
            )
        )

    return {
        "patient_id": patient_id_value,
        "age": age_value,
        "symptoms": list(symptoms_value),
    }
