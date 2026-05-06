def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    enabled_workers = [w["name"] for w in workers if w.get("enabled", True)]
    if not enabled_workers:
        raise ValueError("No enabled workers available.")

    result = []
    if capacities is None:
        for i, job in enumerate(jobs):
            worker = enabled_workers[i % len(enabled_workers)]
            result.append({"job": job, "worker": worker})
    else:
        counts: dict[str, int] = {name: 0 for name in enabled_workers}
        rr_index = 0
        for job in jobs:
            # Try each worker at most len(enabled_workers) times to find one
            # with remaining capacity.
            assigned = False
            for _ in range(len(enabled_workers)):
                worker = enabled_workers[rr_index % len(enabled_workers)]
                rr_index += 1
                cap = capacities.get(worker)
                if cap is None or counts[worker] < cap:
                    counts[worker] += 1
                    result.append({"job": job, "worker": worker})
                    assigned = True
                    break
            # If no worker could take the job, omit it (overflow).
            _ = assigned  # explicit acknowledgement that omission is intentional

    return result
