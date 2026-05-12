"""
Round-robin scheduler module.

Provides assign_round_robin to distribute jobs across enabled workers
in a round-robin fashion.
"""


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """
    Assign jobs to enabled workers in round-robin order.

    Parameters
    ----------
    workers : list[dict]
        Each dict must have a "name" key and an optional "enabled" key
        (defaults to True when absent).
    jobs : list[str]
        Job identifiers to be assigned, processed in input order.

    Returns
    -------
    list[dict]
        A list of {"job": str, "worker": str} mappings, one per job.

    Raises
    ------
    ValueError
        If there are no enabled workers.
    """
    enabled_workers = [
        w["name"] for w in workers if w.get("enabled", True)
    ]

    if not enabled_workers:
        raise ValueError("No enabled workers available to assign jobs.")

    result = []
    num_workers = len(enabled_workers)

    for index, job in enumerate(jobs):
        worker_name = enabled_workers[index % num_workers]
        result.append({"job": job, "worker": worker_name})

    return result
