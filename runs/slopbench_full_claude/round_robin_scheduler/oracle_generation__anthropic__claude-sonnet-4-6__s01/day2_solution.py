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
    counts: dict[str, int] = {}
    rr_index = 0

    for job in jobs:
        # Try each worker at most len(active) times to find one with capacity.
        assigned = False
        for _ in range(len(active)):
            worker = active[rr_index % len(active)]
            rr_index += 1
            if capacities is not None and worker in capacities:
                if counts.get(worker, 0) >= capacities[worker]:
                    continue  # This worker is full; try the next one.
            counts[worker] = counts.get(worker, 0) + 1
            result.append({"job": job, "worker": worker})
            assigned = True
            break

        # If no worker could take the job, omit it (overflow).
        if not assigned:
            # Advance rr_index so the next job starts from the right position.
            # rr_index was already advanced len(active) times in the loop above;
            # no additional adjustment needed.
            pass

    return result
