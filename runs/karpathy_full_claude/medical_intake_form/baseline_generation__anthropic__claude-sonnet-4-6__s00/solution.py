"""
medical_intake_form.py

Validates a medical intake form payload and returns a cleaned dictionary.
"""


def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake form payload.

    Required fields:
        - patient_id (str): Non-empty string identifying the patient.
        - age (int): Integer >= 0 representing the patient's age.
        - symptoms (list[str]): List of symptom strings (may be empty).

    Parameters
    ----------
    payload : dict
        The raw intake form data.

    Returns
    -------
    dict
        A cleaned dictionary containing only the validated required fields.

    Raises
    ------
    ValueError
        If any required field is missing or fails validation, with the
        name of the offending field included in the error message.
    TypeError
        If *payload* is not a dict.
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

    # ------------------------------------------------------------------ #
    # patient_id validation
    # ------------------------------------------------------------------ #
    if "patient_id" not in payload:
        raise ValueError("patient_id")

    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("patient_id")
    patient_id = patient_id.strip()
    if not patient_id:
        raise ValueError("patient_id")

    # ------------------------------------------------------------------ #
    # age validation
    # ------------------------------------------------------------------ #
    if "age" not in payload:
        raise ValueError("age")

    age = payload["age"]
    # Reject booleans (bool is a subclass of int in Python)
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("age")
    if age < 0:
        raise ValueError("age")

    # ------------------------------------------------------------------ #
    # symptoms validation
    # ------------------------------------------------------------------ #
    if "symptoms" not in payload:
        raise ValueError("symptoms")

    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("symptoms")
    cleaned_symptoms = []
    for item in symptoms:
        if not isinstance(item, str):
            raise ValueError("symptoms")
        cleaned_symptoms.append(item)

    # ------------------------------------------------------------------ #
    # Return cleaned payload
    # ------------------------------------------------------------------ #
    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": cleaned_symptoms,
    }
