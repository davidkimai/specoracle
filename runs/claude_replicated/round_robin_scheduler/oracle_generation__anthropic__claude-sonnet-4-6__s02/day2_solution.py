"""Round-robin job scheduler."""


def _enabled_workers(workers: list[dict]) -> list[str]:
    return [w["name"] for w in workers if w.get("enabled", True)]


def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order.

    Args:
        workers: List of worker dicts with "name" and optional "enabled" keys.
        jobs: List of job names to assign.
        capacities: Optional mapping of worker name to maximum number of jobs.
            Workers missing from the mapping have no cap. Jobs that cannot be
            assigned because all workers have reached their capacity are omitted.

    Returns:
        List of {"job": str, "worker": str} dicts in input job order.

    Raises:
        ValueError: If there are no enabled workers.
    """
    active = _enabled_workers(workers)
    if not active:
        raise ValueError("No enabled workers available.")

    if capacities is None:
        return [
            {"job": job, "worker": active[index % len(active)]}
            for index, job in enumerate(jobs)
        ]

    # Track how many jobs each worker has received so far.
    assigned_counts: dict[str, int] = {name: 0 for name in active}
    result: list[dict] = []
    rr_index = 0  # current position in the round-robin cycle

    for job in jobs:
        # Try each worker in the cycle at most len(active) times to find one
        # that still has capacity.
        assigned = False
        for _ in range(len(active)):
            worker = active[rr_index % len(active)]
            rr_index += 1
            cap = capacities.get(worker)
            if cap is None or assigned_counts[worker] < cap:
                assigned_counts[worker] += 1
                result.append({"job": job, "worker": worker})
                assigned = True
                break

        if not assigned:
            # All workers are at capacity; skip this job (omit from output).
            pass

    return result
