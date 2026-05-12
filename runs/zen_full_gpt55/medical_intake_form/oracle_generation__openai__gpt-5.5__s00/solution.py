__all__ = ["validate_intake"]


_MISSING = object()


def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake payload and return a clean dictionary containing
    only the required fields: patient_id, age, and symptoms.

    Raises:
        ValueError: if payload or any required field is invalid. The error
        message names the field or fields that failed validation.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    errors = []

    patient_id = payload.get("patient_id", _MISSING)
    age = payload.get("age", _MISSING)
    symptoms = payload.get("symptoms", _MISSING)

    if patient_id is _MISSING:
        errors.append("patient_id is required")
    elif not isinstance(patient_id, str):
        errors.append("patient_id must be a str")

    if age is _MISSING:
        errors.append("age is required")
    elif not isinstance(age, int) or isinstance(age, bool):
        errors.append("age must be an int")
    elif age < 0:
        errors.append("age must be >= 0")

    if symptoms is _MISSING:
        errors.append("symptoms is required")
    elif not isinstance(symptoms, list):
        errors.append("symptoms must be a list[str]")
    else:
        for index, symptom in enumerate(symptoms):
            if not isinstance(symptom, str):
                errors.append(f"symptoms must contain only str values; invalid item at index {index}")
                break

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
