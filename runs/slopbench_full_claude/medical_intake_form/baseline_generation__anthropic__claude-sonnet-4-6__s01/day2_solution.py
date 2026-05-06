"""
medical_intake_form.py

Provides validate_intake(payload: dict) -> dict for validating and cleaning
medical intake form submissions.
"""


def validate_intake(
    payload: dict,
    optional_fields: "dict[str, callable] | None" = None,
) -> dict:
    """
    Validate a medical intake form payload.

    Required fields:
      - patient_id: non-empty str
      - age: int >= 0
      - symptoms: list of str (may be empty, but must be a list)

    Optional fields:
      - optional_fields: a dict mapping field names to validator callables.
        Each callable receives the field value and should raise ValueError
        (naming the field) or return the cleaned value.  Optional fields are
        validated only when present in payload and included in the output when
        valid.  Errors must name the optional field.

    Returns a clean dict containing exactly the validated fields.
    Raises ValueError naming the first bad field encountered.
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

    # --- patient_id ---
    if "patient_id" not in payload:
        raise ValueError("patient_id")
    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("patient_id")
    if not patient_id.strip():
        raise ValueError("patient_id")

    # --- age ---
    if "age" not in payload:
        raise ValueError("age")
    age = payload["age"]
    # Reject booleans (bool is a subclass of int in Python)
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("age")
    if age < 0:
        raise ValueError("age")

    # --- symptoms ---
    if "symptoms" not in payload:
        raise ValueError("symptoms")
    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("symptoms")
    for item in symptoms:
        if not isinstance(item, str):
            raise ValueError("symptoms")

    result = {
        "patient_id": patient_id,
        "age": age,
        "symptoms": list(symptoms),
    }

    # --- optional fields ---
    if optional_fields:
        for field_name, validator in optional_fields.items():
            if field_name not in payload:
                continue
            raw_value = payload[field_name]
            try:
                cleaned_value = validator(raw_value)
            except ValueError:
                raise ValueError(field_name)
            except Exception:
                raise ValueError(field_name)
            result[field_name] = cleaned_value

    return result
