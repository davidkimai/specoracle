"""Medical intake form validation module."""


def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake payload and return a clean dictionary.

    Required fields:
      - patient_id: str
      - age: int >= 0
      - symptoms: list[str]

    Raises:
        ValueError: if payload or any required field is invalid. The error
        message names the invalid field or fields.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    invalid_fields = []

    has_patient_id = "patient_id" in payload
    has_age = "age" in payload
    has_symptoms = "symptoms" in payload

    patient_id = payload.get("patient_id")
    age = payload.get("age")
    symptoms = payload.get("symptoms")

    if not has_patient_id or not isinstance(patient_id, str):
        invalid_fields.append("patient_id")

    if not has_age or not isinstance(age, int) or isinstance(age, bool) or age < 0:
        invalid_fields.append("age")

    if not has_symptoms or not isinstance(symptoms, list):
        invalid_fields.append("symptoms")
    elif not all(isinstance(symptom, str) for symptom in symptoms):
        invalid_fields.append("symptoms")

    if invalid_fields:
        raise ValueError("invalid field(s): " + ", ".join(invalid_fields))

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
