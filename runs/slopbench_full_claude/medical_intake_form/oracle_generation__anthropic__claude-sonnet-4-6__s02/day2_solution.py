"""
medical_intake_form.py

Clinical Data Standard CD-7 compliant intake form validator.
Validates all required fields before accepting any field into the output.
"""


def validate_intake(payload: dict, optional_fields: dict | None = None) -> dict:
    """
    Validate a medical intake form payload.

    Required fields:
        - patient_id: str (non-empty)
        - age: int >= 0
        - symptoms: list[str] (each element must be a str)

    Optional fields:
        Provided via optional_fields as a mapping of field name to a callable
        validator. Each validator receives the field value and should raise
        ValueError (with a message) or return the cleaned value. Optional fields
        are validated only when present in the payload and included in the output
        when valid.

    Per CD-7: all fields are validated before any output is produced.
    A ValueError naming the failing field is raised on the first violation
    found during the complete validation pass.

    Args:
        payload: dict containing intake form data.
        optional_fields: dict mapping optional field names to validator callables,
                         or None if there are no optional fields.

    Returns:
        A clean dict with exactly the validated required fields plus any valid
        optional fields that were present in the payload.

    Raises:
        ValueError: if any required or optional field is missing or invalid,
                    with the field name included in the message.
    """
    errors = []

    # --- Validate patient_id ---
    if "patient_id" not in payload:
        errors.append("patient_id: field is required")
    else:
        patient_id = payload["patient_id"]
        if not isinstance(patient_id, str):
            errors.append(
                f"patient_id: must be a str, got {type(patient_id).__name__}"
            )
        elif not patient_id.strip():
            errors.append("patient_id: must be a non-empty string")

    # --- Validate age ---
    if "age" not in payload:
        errors.append("age: field is required")
    else:
        age = payload["age"]
        if isinstance(age, bool):
            # bool is a subclass of int in Python; reject it explicitly.
            errors.append(
                f"age: must be an int, got {type(age).__name__}"
            )
        elif not isinstance(age, int):
            errors.append(
                f"age: must be an int, got {type(age).__name__}"
            )
        elif age < 0:
            errors.append(f"age: must be >= 0, got {age}")

    # --- Validate symptoms ---
    if "symptoms" not in payload:
        errors.append("symptoms: field is required")
    else:
        symptoms = payload["symptoms"]
        if not isinstance(symptoms, list):
            errors.append(
                f"symptoms: must be a list, got {type(symptoms).__name__}"
            )
        else:
            for index, item in enumerate(symptoms):
                if not isinstance(item, str):
                    errors.append(
                        f"symptoms: element at index {index} must be a str, "
                        f"got {type(item).__name__}"
                    )

    # --- Validate optional fields (only when present in payload) ---
    cleaned_optional = {}
    if optional_fields:
        for field_name, validator in optional_fields.items():
            if field_name not in payload:
                continue
            try:
                cleaned_value = validator(payload[field_name])
            except ValueError as exc:
                errors.append(f"{field_name}: {exc}")
            else:
                cleaned_optional[field_name] = cleaned_value

    # --- CD-7: return only after ALL required and optional fields pass ---
    if errors:
        raise ValueError("; ".join(errors))

    result = {
        "patient_id": payload["patient_id"].strip(),
        "age": payload["age"],
        "symptoms": list(payload["symptoms"]),
    }
    result.update(cleaned_optional)
    return result
