"""Round-robin scheduler module."""


def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order.

    Args:
        workers: List of worker dicts with "name" and optional "enabled" fields.
        jobs: List of job strings to assign.
        capacities: Optional mapping of worker name to maximum number of jobs
            that worker may receive. Workers absent from the mapping have no
            cap. Jobs that cannot be assigned due to capacity limits are
            omitted from the result.

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
    assigned_counts: dict[str, int] = {name: 0 for name in enabled_workers}
    num_workers = len(enabled_workers)
    index = 0  # round-robin pointer

    for job in jobs:
        # Try each worker starting from the current round-robin position.
        assigned = False
        for offset in range(num_workers):
            worker_name = enabled_workers[(index + offset) % num_workers]
            cap = capacities.get(worker_name) if capacities is not None else None
            if cap is None or assigned_counts[worker_name] < cap:
                result.append({"job": job, "worker": worker_name})
                assigned_counts[worker_name] += 1
                # Advance the round-robin pointer past the chosen worker.
                index = (index + offset + 1) % num_workers
                assigned = True
                break
        if not assigned:
            # All workers are at capacity; omit this job.
            pass

    return result
