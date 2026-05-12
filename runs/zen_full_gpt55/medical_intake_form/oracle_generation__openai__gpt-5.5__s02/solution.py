def validate_intake(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    errors = []

    if "patient_id" not in payload:
        errors.append("patient_id is required")
        patient_id_valid = False
    else:
        patient_id = payload["patient_id"]
        patient_id_valid = isinstance(patient_id, str)
        if not patient_id_valid:
            errors.append("patient_id must be a str")

    if "age" not in payload:
        errors.append("age is required")
        age_valid = False
    else:
        age = payload["age"]
        age_valid = isinstance(age, int) and not isinstance(age, bool) and age >= 0
        if not age_valid:
            errors.append("age must be an int >= 0")

    if "symptoms" not in payload:
        errors.append("symptoms is required")
        symptoms_valid = False
    else:
        symptoms = payload["symptoms"]
        symptoms_valid = isinstance(symptoms, list) and all(
            isinstance(item, str) for item in symptoms
        )
        if not symptoms_valid:
            errors.append("symptoms must be a list of str")

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }
