from typing import Any


def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake payload and return a clean dictionary containing
    only the required fields: patient_id, age, and symptoms.

    Raises:
        ValueError: If payload or any required field is missing or invalid.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload")

    if "patient_id" not in payload:
        raise ValueError("patient_id")
    if "age" not in payload:
        raise ValueError("age")
    if "symptoms" not in payload:
        raise ValueError("symptoms")

    patient_id: Any = payload["patient_id"]
    age: Any = payload["age"]
    symptoms: Any = payload["symptoms"]

    if not isinstance(patient_id, str):
        raise ValueError("patient_id")

    if not isinstance(age, int) or isinstance(age, bool) or age < 0:
        raise ValueError("age")

    if not isinstance(symptoms, list):
        raise ValueError("symptoms")

    for symptom in symptoms:
        if not isinstance(symptom, str):
            raise ValueError("symptoms")

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
