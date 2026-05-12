from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Return alphabetized parallel execution batches for dependency tasks.

    Each mapping entry is interpreted as task -> prerequisites. Tasks that appear
    only as prerequisites are included. The input mapping and lists are not
    mutated. Raises ValueError if the dependency graph contains a cycle.
    """
    all_tasks: set[str] = set(dependencies)
    for prerequisites in dependencies.values():
        all_tasks.update(prerequisites)

    dependents: dict[str, set[str]] = {task: set() for task in all_tasks}
    remaining_prerequisites: dict[str, int] = {task: 0 for task in all_tasks}

    for task, prerequisites in dependencies.items():
        unique_prerequisites = set(prerequisites)
        remaining_prerequisites[task] = len(unique_prerequisites)
        for prerequisite in unique_prerequisites:
            dependents[prerequisite].add(task)

    ready = sorted(
        task for task, count in remaining_prerequisites.items() if count == 0
    )
    batches: list[list[str]] = []
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        next_ready: list[str] = []
        for task in batch:
            for dependent in dependents[task]:
                remaining_prerequisites[dependent] -= 1
                if remaining_prerequisites[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed_count != len(all_tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches
