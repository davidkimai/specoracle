"""Round-robin job scheduler."""


def _enabled_workers(workers: list[dict]) -> list[str]:
    return [w["name"] for w in workers if w.get("enabled", True)]


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order.

    Args:
        workers: List of dicts with "name" and optional "enabled" fields.
        jobs: List of job identifiers to assign.

    Returns:
        List of {"job": str, "worker": str} dicts in job input order.

    Raises:
        ValueError: If there are no enabled workers.
    """
    active = _enabled_workers(workers)
    if not active:
        raise ValueError("No enabled workers available.")

    return [
        {"job": job, "worker": active[index % len(active)]}
        for index, job in enumerate(jobs)
    ]
