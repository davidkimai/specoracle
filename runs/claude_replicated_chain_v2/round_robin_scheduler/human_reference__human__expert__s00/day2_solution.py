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
            # Try each worker at most len(enabled) times to find one with capacity
            assigned = False
            for _ in range(len(enabled)):
                worker = enabled[rr_index % len(enabled)]
                rr_index += 1
                cap = capacities.get(worker)
                if cap is None or counts[worker] < cap:
                    assignments.append({"job": job, "worker": worker})
                    counts[worker] += 1
                    assigned = True
                    break
            # If no worker has capacity, the job is omitted (overflow)
            if not assigned:
                # Advance round-robin index as if we had assigned (skip the job)
                pass

    return assignments
