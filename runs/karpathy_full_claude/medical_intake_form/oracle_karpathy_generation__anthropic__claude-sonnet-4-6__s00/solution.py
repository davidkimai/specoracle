"""
medical_intake_form.py

Clinical Data Standard CD-7 compliant intake form validator.
Validates all required fields before accepting any into the output.
"""


def validate_intake(payload: dict) -> dict:
    """
    Validate a medical intake form payload.

    Required fields:
        - patient_id: str (non-empty)
        - age: int >= 0
        - symptoms: list[str] (each element must be a str)

    All fields are validated before any are accepted into the output.
    Raises ValueError naming the first bad field encountered, but only
    after all fields have been checked (partial validation is not permitted).

    Args:
        payload: dict containing intake form data.

    Returns:
        A clean dict with the validated required fields.

    Raises:
        ValueError: If any required field is missing or fails validation,
                    with the field name included in the error message.
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

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
    elif isinstance(age, bool):
        # bool is a subclass of int; reject it explicitly
        errors.append("age: must be an int, not bool")
    elif not isinstance(age, int):
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
                break  # report the first bad element; field name is still named

    # CD-7: return only after all required fields pass
    if errors:
        raise ValueError("; ".join(errors))

    return {
        "patient_id": patient_id.strip(),
        "age": age,
        "symptoms": list(symptoms),
    }
