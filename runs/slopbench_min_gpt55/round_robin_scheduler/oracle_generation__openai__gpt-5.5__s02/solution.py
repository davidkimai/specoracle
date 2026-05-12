def _enabled_worker_names(workers: list[dict]) -> list[str]:
    if not isinstance(workers, list):
        raise TypeError("workers must be a list of dictionaries")

    names: list[str] = []

    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            raise TypeError(f"workers[{index}] must be a dictionary")

        if "name" not in worker:
            raise ValueError(f"workers[{index}] is missing required field 'name'")

        name = worker["name"]
        if not isinstance(name, str):
            raise TypeError(f"workers[{index}]['name'] must be a string")

        enabled = worker.get("enabled", True)
        if not isinstance(enabled, bool):
            raise TypeError(f"workers[{index}]['enabled'] must be a boolean")

        if enabled:
            names.append(name)

    return names


def _validated_jobs(jobs: list[str]) -> list[str]:
    if not isinstance(jobs, list):
        raise TypeError("jobs must be a list of strings")

    for index, job in enumerate(jobs):
        if not isinstance(job, str):
            raise TypeError(f"jobs[{index}] must be a string")

    return list(jobs)


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    worker_names = _enabled_worker_names(workers)
    if not worker_names:
        raise ValueError("there are no enabled workers")

    validated_jobs = _validated_jobs(jobs)
    worker_count = len(worker_names)

    return [
        {"job": job, "worker": worker_names[index % worker_count]}
        for index, job in enumerate(validated_jobs)
    ]
