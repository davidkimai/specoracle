def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake payload and return a clean dictionary containing only
    the validated fields.

    Required fields:
      - patient_id: str
      - age: int >= 0
      - symptoms: list[str]

    Raises:
        ValueError: If the payload or any required field is missing or invalid.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload")

    if "patient_id" not in payload:
        raise ValueError("patient_id")
    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("patient_id")

    if "age" not in payload:
        raise ValueError("age")
    age = payload["age"]
    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        raise ValueError("age")

    if "symptoms" not in payload:
        raise ValueError("symptoms")
    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("symptoms")
    if not all(isinstance(symptom, str) for symptom in symptoms):
        raise ValueError("symptoms")

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
