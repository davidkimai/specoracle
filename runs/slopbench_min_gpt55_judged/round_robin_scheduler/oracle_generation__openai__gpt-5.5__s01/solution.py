def _require_list(value: object, parameter_name: str) -> list:
    if not isinstance(value, list):
        raise TypeError(f"{parameter_name} must be a list")
    return value


def _worker_name(worker: dict, index: int) -> str:
    if "name" not in worker:
        raise ValueError(f"workers[{index}] is missing required field 'name'")

    name = worker["name"]
    if not isinstance(name, str):
        raise TypeError(f"workers[{index}]['name'] must be a string")

    return name


def _worker_enabled(worker: dict, index: int) -> bool:
    enabled = worker.get("enabled", True)
    if not isinstance(enabled, bool):
        raise TypeError(f"workers[{index}]['enabled'] must be a boolean when present")

    return enabled


def _enabled_worker_names(workers: list[dict]) -> list[str]:
    names: list[str] = []

    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            raise TypeError(f"workers[{index}] must be a dict")

        name = _worker_name(worker, index)
        if _worker_enabled(worker, index):
            names.append(name)

    return names


def _validated_jobs(jobs: list[str]) -> list[str]:
    validated: list[str] = []

    for index, job in enumerate(jobs):
        if not isinstance(job, str):
            raise TypeError(f"jobs[{index}] must be a string")
        validated.append(job)

    return validated


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    workers = _require_list(workers, "workers")
    jobs = _require_list(jobs, "jobs")

    worker_names = _enabled_worker_names(workers)
    if not worker_names:
        raise ValueError("there are no enabled workers")

    validated_jobs = _validated_jobs(jobs)
    worker_count = len(worker_names)

    return [
        {"job": job, "worker": worker_names[index % worker_count]}
        for index, job in enumerate(validated_jobs)
    ]
