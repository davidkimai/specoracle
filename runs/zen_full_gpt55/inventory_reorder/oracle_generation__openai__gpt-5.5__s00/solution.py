def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_item(item: object) -> bool:
    if not isinstance(item, dict):
        return False

    required_keys = ("sku", "on_hand", "target", "case_pack")
    if any(key not in item for key in required_keys):
        return False

    if not isinstance(item["sku"], str):
        return False

    if not _is_plain_int(item["on_hand"]):
        return False

    if not _is_plain_int(item["target"]):
        return False

    if not _is_plain_int(item["case_pack"]):
        return False

    return True


def _rounded_case_quantity(deficit: int, case_pack: int) -> int:
    return ((deficit + case_pack - 1) // case_pack) * case_pack


def _sales_velocity_for_sku(sales_velocity: dict[str, int], sku: str) -> int:
    velocity = sales_velocity.get(sku, 0)

    if not _is_plain_int(velocity):
        raise TypeError(f"sales_velocity for sku {sku!r} must be an integer")

    return velocity


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    if not isinstance(sales_velocity, dict):
        raise TypeError("sales_velocity must be a dict")

    rows = []

    for item in items:
        if not _valid_item(item):
            continue

        sku = item["sku"]
        case_pack = item["case_pack"]

        if case_pack <= 0:
            continue

        velocity = _sales_velocity_for_sku(sales_velocity, sku)
        if velocity <= 0:
            continue

        on_hand = item["on_hand"]
        target = item["target"]

        if on_hand >= target:
            continue

        deficit = target - on_hand
        rows.append(
            {
                "sku": sku,
                "reorder_quantity": _rounded_case_quantity(deficit, case_pack),
            }
        )

    return sorted(rows, key=lambda row: row["sku"])
