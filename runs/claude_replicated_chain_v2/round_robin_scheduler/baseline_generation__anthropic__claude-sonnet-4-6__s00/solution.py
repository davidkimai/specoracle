"""Round-robin scheduler module."""


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order.

    Args:
        workers: List of worker dicts with "name" and optional "enabled" fields.
        jobs: List of job strings to assign.

    Returns:
        List of dicts shaped as {"job": str, "worker": str}.

    Raises:
        ValueError: If there are no enabled workers.
    """
    enabled_workers = [
        w["name"] for w in workers if w.get("enabled", True)
    ]

    if not enabled_workers:
        raise ValueError("No enabled workers available.")

    result = []
    num_workers = len(enabled_workers)

    for index, job in enumerate(jobs):
        worker_name = enabled_workers[index % num_workers]
        result.append({"job": job, "worker": worker_name})

    return result
