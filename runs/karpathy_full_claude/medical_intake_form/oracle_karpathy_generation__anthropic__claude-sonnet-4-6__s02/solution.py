"""
medical_intake_form.py

Clinical Data Standard CD-7 compliant intake form validation.
Validates all required fields before accepting any field into the output.
"""


def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake form payload.

    Required fields:
        - patient_id: str (non-empty)
        - age: int >= 0
        - symptoms: list[str] (each element must be a str)

    Validates ALL fields before returning. Raises ValueError naming the
    bad field if any validation fails. Partial validation is not permitted.

    Args:
        payload: dict containing the intake form data.

    Returns:
        A clean dict with validated fields: patient_id, age, symptoms.

    Raises:
        ValueError: If any required field is missing or invalid, naming
                    the specific field that failed validation.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    errors = []

    # Validate patient_id
    patient_id = payload.get("patient_id", _MISSING := object())
    if patient_id is _MISSING:
        errors.append("patient_id: field is required")
    elif not isinstance(patient_id, str):
        errors.append("patient_id: must be a str")
    elif not patient_id.strip():
        errors.append("patient_id: must not be empty")

    # Validate age
    age = payload.get("age", _MISSING)
    if age is _MISSING:
        errors.append("age: field is required")
    elif not isinstance(age, int) or isinstance(age, bool):
        errors.append("age: must be an int")
    elif age < 0:
        errors.append("age: must be >= 0")

    # Validate symptoms
    symptoms = payload.get("symptoms", _MISSING)
    if symptoms is _MISSING:
        errors.append("symptoms: field is required")
    elif not isinstance(symptoms, list):
        errors.append("symptoms: must be a list")
    else:
        for index, item in enumerate(symptoms):
            if not isinstance(item, str):
                errors.append(f"symptoms: element at index {index} must be a str")
                break

    # CD-7: Return only after ALL required fields pass; never partial.
    if errors:
        # Name the first (and most relevant) bad field in the exception message,
        # but include all errors so the caller has full context.
        raise ValueError("; ".join(errors))

    # Build and return the clean output dict.
    clean = {
        "patient_id": payload["patient_id"].strip(),
        "age": payload["age"],
        "symptoms": list(payload["symptoms"]),
    }
    return clean
