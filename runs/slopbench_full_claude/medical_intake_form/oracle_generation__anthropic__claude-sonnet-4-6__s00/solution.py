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
    Raises ValueError naming the first field that fails validation.

    Parameters
    ----------
    payload : dict
        Raw intake form data.

    Returns
    -------
    dict
        Cleaned and validated intake data containing exactly the
        required fields.

    Raises
    ------
    ValueError
        If any required field is missing or invalid, with the field
        name included in the error message.
    TypeError
        If payload is not a dict.
    """
    if not isinstance(payload, dict):
        raise TypeError(
            f"payload must be a dict, got {type(payload).__name__!r}"
        )

    errors = []

    # --- Validate patient_id ---
    if "patient_id" not in payload:
        errors.append("patient_id: field is required")
    else:
        patient_id = payload["patient_id"]
        if not isinstance(patient_id, str):
            errors.append(
                f"patient_id: expected str, got {type(patient_id).__name__!r}"
            )
        elif not patient_id.strip():
            errors.append("patient_id: must be a non-empty string")

    # --- Validate age ---
    if "age" not in payload:
        errors.append("age: field is required")
    else:
        age = payload["age"]
        # bool is a subclass of int in Python; reject booleans explicitly.
        if isinstance(age, bool) or not isinstance(age, int):
            errors.append(
                f"age: expected int, got {type(age).__name__!r}"
            )
        elif age < 0:
            errors.append(f"age: must be >= 0, got {age!r}")

    # --- Validate symptoms ---
    if "symptoms" not in payload:
        errors.append("symptoms: field is required")
    else:
        symptoms = payload["symptoms"]
        if not isinstance(symptoms, list):
            errors.append(
                f"symptoms: expected list, got {type(symptoms).__name__!r}"
            )
        else:
            for index, item in enumerate(symptoms):
                if not isinstance(item, str):
                    errors.append(
                        f"symptoms: element at index {index} must be str, "
                        f"got {type(item).__name__!r}"
                    )

    # --- CD-7: Return only after ALL required fields pass ---
    if errors:
        raise ValueError("; ".join(errors))

    return {
        "patient_id": payload["patient_id"].strip(),
        "age": payload["age"],
        "symptoms": list(payload["symptoms"]),
    }
