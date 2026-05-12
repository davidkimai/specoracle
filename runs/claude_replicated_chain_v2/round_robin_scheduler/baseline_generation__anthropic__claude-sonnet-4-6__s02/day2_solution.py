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
        capacities: Optional mapping of worker name to maximum job count.
            Workers missing from the mapping have no cap. Jobs that would
            exceed all remaining capacities are omitted.

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

    # Track how many jobs each worker has been assigned (only when caps apply).
    assigned_counts: dict[str, int] = {name: 0 for name in enabled_workers}

    result = []
    num_workers = len(enabled_workers)
    rr_index = 0  # Tracks position in the round-robin cycle.

    for job in jobs:
        # Find the next worker that still has capacity.
        assigned = False
        for _ in range(num_workers):
            worker_name = enabled_workers[rr_index % num_workers]
            rr_index += 1

            if capacities is not None:
                cap = capacities.get(worker_name)
                if cap is not None and assigned_counts[worker_name] >= cap:
                    # This worker is full; try the next one.
                    continue

            # Worker has capacity (or caps not in use).
            assigned_counts[worker_name] += 1
            result.append({"job": job, "worker": worker_name})
            assigned = True
            break

        # If no worker could accept the job, omit it (overflow).
        if not assigned:
            pass

    return result
