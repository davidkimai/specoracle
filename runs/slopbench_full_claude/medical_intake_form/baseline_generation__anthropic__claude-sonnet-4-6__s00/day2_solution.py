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
        - patient_id (str): Non-empty string identifier for the patient.
        - age (int): Integer >= 0.
        - symptoms (list[str]): List of symptom strings (may be empty,
          but each element must be a non-empty string).

    Optional fields:
        - optional_fields (dict[str, callable] | None): A mapping of field
          names to validator callables. Each callable receives the field value
          and should return the cleaned/validated value, or raise ValueError
          if the value is invalid. Optional fields are only validated when
          present in the payload; if present and valid, they are included in
          the returned dict.

    Returns:
        A clean dict containing the validated required fields and any valid
        optional fields that were present in the payload.

    Raises:
        ValueError: If any required field is missing or fails validation,
                    or if an optional field fails its validator, with a
                    message naming the offending field.
        TypeError:  If payload is not a dict.
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

    # --- patient_id ---
    if "patient_id" not in payload:
        raise ValueError("patient_id")
    patient_id = payload["patient_id"]
    if not isinstance(patient_id, str):
        raise ValueError("patient_id")
    patient_id = patient_id.strip()
    if not patient_id:
        raise ValueError("patient_id")

    # --- age ---
    if "age" not in payload:
        raise ValueError("age")
    age = payload["age"]
    # Reject booleans (bool is a subclass of int in Python)
    if isinstance(age, bool):
        raise ValueError("age")
    if not isinstance(age, int):
        raise ValueError("age")
    if age < 0:
        raise ValueError("age")

    # --- symptoms ---
    if "symptoms" not in payload:
        raise ValueError("symptoms")
    symptoms = payload["symptoms"]
    if not isinstance(symptoms, list):
        raise ValueError("symptoms")
    cleaned_symptoms = []
    for item in symptoms:
        if not isinstance(item, str):
            raise ValueError("symptoms")
        item_stripped = item.strip()
        if not item_stripped:
            raise ValueError("symptoms")
        cleaned_symptoms.append(item_stripped)

    result = {
        "patient_id": patient_id,
        "age": age,
        "symptoms": cleaned_symptoms,
    }

    # --- optional fields ---
    if optional_fields:
        for field_name, validator in optional_fields.items():
            if field_name not in payload:
                continue
            try:
                cleaned_value = validator(payload[field_name])
            except (ValueError, TypeError):
                raise ValueError(field_name)
            result[field_name] = cleaned_value

    return result
