"""Round-robin job scheduler."""


def _enabled_workers(workers: list[dict]) -> list[str]:
    return [w["name"] for w in workers if w.get("enabled", True)]


def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    active = _enabled_workers(workers)
    if not active:
        raise ValueError("No enabled workers available.")

    result = []
    assigned_counts: dict[str, int] = {name: 0 for name in active}
    index = 0  # round-robin position across active workers

    for job in jobs:
        # Find the next worker with remaining capacity, starting from current index.
        # We may need to skip up to len(active) workers if some are full.
        assigned = False
        for _ in range(len(active)):
            worker = active[index % len(active)]
            index += 1
            cap = capacities.get(worker) if capacities is not None else None
            if cap is None or assigned_counts[worker] < cap:
                assigned_counts[worker] += 1
                result.append({"job": job, "worker": worker})
                assigned = True
                break

        if not assigned:
            # All workers are at capacity; omit this job (and remaining jobs
            # since capacities will only stay the same or be more exhausted).
            # Per requirement, overflow jobs are omitted.
            continue

    return result
