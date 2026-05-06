"""Round-robin job scheduler module."""

from __future__ import annotations


def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order.

    Parameters
    ----------
    workers:
        List of worker dicts, each with a "name" key and an optional
        "enabled" key (defaults to True).
    jobs:
        List of job identifiers to assign.
    capacities:
        Optional mapping of worker name to maximum number of jobs that
        worker may receive.  Workers absent from the mapping have no cap.
        Jobs that cannot be assigned because every eligible worker has
        reached capacity are omitted from the result.

    Returns
    -------
    list[dict]
        A list of {"job": str, "worker": str} dicts, one per job.

    Raises
    ------
    ValueError
        If there are no enabled workers.
    """
    enabled_workers = [w["name"] for w in workers if w.get("enabled", True)]

    if not enabled_workers:
        raise ValueError("No enabled workers available to assign jobs.")

    result = []
    num_workers = len(enabled_workers)

    # Track how many jobs each worker has been assigned (only needed when
    # capacities are provided).
    assigned_counts: dict[str, int] = {name: 0 for name in enabled_workers}

    # Round-robin index; advances independently of the job loop so that
    # skipping a capped worker doesn't restart from the same position.
    rr_index = 0

    for job in jobs:
        if capacities is None:
            # Original behaviour: simple modulo round-robin.
            worker_name = enabled_workers[rr_index % num_workers]
            result.append({"job": job, "worker": worker_name})
            rr_index += 1
        else:
            # Find the next worker that still has capacity, cycling at most
            # num_workers times before declaring the job unassignable.
            assigned = False
            for _ in range(num_workers):
                candidate = enabled_workers[rr_index % num_workers]
                rr_index += 1
                cap = capacities.get(candidate)
                if cap is None or assigned_counts[candidate] < cap:
                    assigned_counts[candidate] += 1
                    result.append({"job": job, "worker": candidate})
                    assigned = True
                    break
            # If no worker could take the job, omit it (overflow).

    return result
