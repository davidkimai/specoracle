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
        workers: List of dicts with "name" and optional "enabled" fields.
        jobs: List of job identifiers to assign.
        capacities: Optional mapping of worker name to max number of jobs.
            Workers missing from the dict have no cap. Jobs that cannot be
            assigned because all workers are at capacity are omitted.

    Returns:
        List of {"job": str, "worker": str} dicts in job input order.

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

    # Track how many jobs each worker has been assigned so far.
    assigned_counts: dict[str, int] = {name: 0 for name in active}
    result: list[dict] = []
    rr_index = 0  # next candidate position in active list

    for job in jobs:
        # Walk round-robin until we find an available worker or exhaust all.
        n = len(active)
        assigned = False
        for _ in range(n):
            worker = active[rr_index % n]
            cap = capacities.get(worker)  # None means no cap
            if cap is None or assigned_counts[worker] < cap:
                result.append({"job": job, "worker": worker})
                assigned_counts[worker] += 1
                rr_index += 1
                assigned = True
                break
            rr_index += 1

        if not assigned:
            # All workers are at capacity; skip (omit) this job.
            pass

    return result
