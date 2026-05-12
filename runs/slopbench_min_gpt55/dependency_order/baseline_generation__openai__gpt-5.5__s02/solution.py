from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Plan tasks into parallelizable batches based on prerequisite dependencies.

    Args:
        dependencies: Mapping from task name to the list of tasks that must be
            completed before that task can run.

    Returns:
        A list of batches. Each batch contains tasks that can run in parallel,
        sorted alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle.
    """
    all_tasks: set[str] = set(dependencies)
    for prerequisites in dependencies.values():
        all_tasks.update(prerequisites)

    remaining_prerequisites: dict[str, set[str]] = {
        task: set(dependencies.get(task, ())) for task in all_tasks
    }

    batches: list[list[str]] = []
    completed: set[str] = set()

    while remaining_prerequisites:
        ready = sorted(
            task
            for task, prerequisites in remaining_prerequisites.items()
            if prerequisites <= completed
        )

        if not ready:
            raise ValueError("dependency graph contains a cycle")

        batches.append(ready)
        completed.update(ready)

        for task in ready:
            del remaining_prerequisites[task]

    return batches
