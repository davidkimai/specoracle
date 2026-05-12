"""Round-robin job scheduler module."""


def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order.

    Args:
        workers: List of worker dicts with "name" and optional "enabled" fields.
        jobs: List of job names to assign.
        capacities: Optional mapping of worker name to maximum number of jobs
            that worker may receive.  Workers absent from the mapping have no
            cap.  Jobs that cannot be assigned due to capacity limits are
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
    num_workers = len(enabled_workers)

    # Track how many jobs each worker has been assigned (used only when
    # capacities is provided).
    assigned_counts: dict[str, int] = {name: 0 for name in enabled_workers}

    index = 0  # round-robin position
    for job in jobs:
        # Try each worker at most num_workers times to find one with capacity.
        assigned = False
        for _ in range(num_workers):
            worker_name = enabled_workers[index % num_workers]
            index += 1

            if capacities is not None:
                cap = capacities.get(worker_name)
                if cap is not None and assigned_counts[worker_name] >= cap:
                    # This worker is full; try the next one.
                    continue

            assigned_counts[worker_name] += 1
            result.append({"job": job, "worker": worker_name})
            assigned = True
            break

        # If no worker could take the job, omit it (overflow).

    return result
