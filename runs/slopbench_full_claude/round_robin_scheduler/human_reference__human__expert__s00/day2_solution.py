def assign_round_robin(
    workers: list[dict],
    jobs: list[str],
    capacities: dict[str, int] | None = None,
) -> list[dict]:
    enabled = [worker["name"] for worker in workers if worker.get("enabled", True)]
    if not enabled:
        raise ValueError("at least one worker must be enabled")

    assignments = []

    if capacities is None:
        for index, job in enumerate(jobs):
            assignments.append({"job": job, "worker": enabled[index % len(enabled)]})
    else:
        counts: dict[str, int] = {name: 0 for name in enabled}
        rr_index = 0
        for job in jobs:
            # Walk through workers in round-robin order looking for available capacity
            assigned = False
            for attempt in range(len(enabled)):
                worker = enabled[(rr_index + attempt) % len(enabled)]
                cap = capacities.get(worker)
                if cap is None or counts[worker] < cap:
                    assignments.append({"job": job, "worker": worker})
                    counts[worker] += 1
                    rr_index = (rr_index + attempt + 1) % len(enabled)
                    assigned = True
                    break
            if not assigned:
                # All workers at capacity; omit this job, advance rr_index normally
                rr_index = (rr_index + 1) % len(enabled)

    return assignments
