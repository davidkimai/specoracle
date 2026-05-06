from __future__ import annotations


def validate_intake(
    payload: dict,
    optional_fields: dict[str, callable] | None = None,
) -> dict:
    errors = []

    if not isinstance(payload.get('patient_id'), str) or not payload.get('patient_id'):
        errors.append('patient_id')
    if not isinstance(payload.get('age'), int) or payload.get('age') < 0:
        errors.append('age')
    symptoms = payload.get('symptoms')
    if not isinstance(symptoms, list) or not all(isinstance(item, str) for item in symptoms):
        errors.append('symptoms')

    validated_optional: dict = {}
    if optional_fields:
        for field, validator in optional_fields.items():
            if field in payload:
                try:
                    result = validator(payload[field])
                except Exception:
                    errors.append(field)
                else:
                    validated_optional[field] = result

    if errors:
        raise ValueError(', '.join(errors))

    output = {
        'patient_id': payload['patient_id'],
        'age': payload['age'],
        'symptoms': list(symptoms),
    }
    output.update(validated_optional)
    return output
