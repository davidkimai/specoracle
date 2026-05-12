def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake payload and return a clean dictionary containing only
    the required fields.

    Required fields:
    - patient_id: str
    - age: int >= 0
    - symptoms: list[str]

    Raises:
        ValueError: if the payload or any required field is invalid. The error
        message names each invalid field.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    missing = object()
    errors = []

    patient_id = payload.get("patient_id", missing)
    age = payload.get("age", missing)
    symptoms = payload.get("symptoms", missing)

    if patient_id is missing:
        errors.append("patient_id is required")
    elif not isinstance(patient_id, str):
        errors.append("patient_id must be a str")

    if age is missing:
        errors.append("age is required")
    elif not isinstance(age, int) or isinstance(age, bool):
        errors.append("age must be an int")
    elif age < 0:
        errors.append("age must be >= 0")

    if symptoms is missing:
        errors.append("symptoms is required")
    elif not isinstance(symptoms, list):
        errors.append("symptoms must be a list[str]")
    else:
        for index, symptom in enumerate(symptoms):
            if not isinstance(symptom, str):
                errors.append(f"symptoms[{index}] must be a str")
                break

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
