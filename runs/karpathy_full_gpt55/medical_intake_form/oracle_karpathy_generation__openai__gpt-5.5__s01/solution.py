"""Medical intake form validation module."""


def validate_intake(payload: dict) -> dict:
    """Validate a medical intake payload and return a clean dictionary.

    Required fields:
    - patient_id: str
    - age: int >= 0
    - symptoms: list[str]

    Raises:
        ValueError: if the payload or any required field is invalid.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    errors = []

    if "patient_id" not in payload:
        errors.append("patient_id is required")
    else:
        patient_id = payload["patient_id"]
        if not isinstance(patient_id, str):
            errors.append("patient_id must be a str")

    if "age" not in payload:
        errors.append("age is required")
    else:
        age = payload["age"]
        if isinstance(age, bool) or not isinstance(age, int):
            errors.append("age must be an int")
        elif age < 0:
            errors.append("age must be >= 0")

    if "symptoms" not in payload:
        errors.append("symptoms is required")
    else:
        symptoms = payload["symptoms"]
        if not isinstance(symptoms, list):
            errors.append("symptoms must be a list[str]")
        else:
            for index, symptom in enumerate(symptoms):
                if not isinstance(symptom, str):
                    errors.append(f"symptoms[{index}] must be a str")

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "patient_id": payload["patient_id"],
        "age": payload["age"],
        "symptoms": list(payload["symptoms"]),
    }
