def validate_intake(payload: dict) -> dict:
    """
    Validate and normalize a medical intake payload.

    Required fields:
      - patient_id: str
      - age: int >= 0
      - symptoms: list[str]

    Returns a clean dict containing only the validated fields.

    Raises:
        ValueError: naming the bad field.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload")

    if "patient_id" not in payload or not isinstance(payload["patient_id"], str):
        raise ValueError("patient_id")

    if (
        "age" not in payload
        or not isinstance(payload["age"], int)
        or isinstance(payload["age"], bool)
        or payload["age"] < 0
    ):
        raise ValueError("age")

    if "symptoms" not in payload or not isinstance(payload["symptoms"], list):
        raise ValueError("symptoms")

    for symptom in payload["symptoms"]:
        if not isinstance(symptom, str):
            raise ValueError("symptoms")

    return {
        "patient_id": payload["patient_id"],
        "age": payload["age"],
        "symptoms": list(payload["symptoms"]),
    }
