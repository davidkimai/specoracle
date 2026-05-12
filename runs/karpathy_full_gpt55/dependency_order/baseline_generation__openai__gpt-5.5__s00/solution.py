from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Plan tasks into parallelizable batches based on prerequisite dependencies.

    Each key in ``dependencies`` is a task, and its value is the list of tasks
    that must be completed before it can run. Tasks that appear only as
    dependencies are included as tasks with no prerequisites.

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

    dependents: dict[str, set[str]] = {task: set() for task in all_tasks}
    for task, prerequisites in dependencies.items():
        for prerequisite in set(prerequisites):
            dependents[prerequisite].add(task)

    ready = sorted(
        task for task, prerequisites in remaining_prerequisites.items()
        if not prerequisites
    )

    batches: list[list[str]] = []
    processed: set[str] = set()

    while ready:
        batch = ready
        batches.append(batch)
        next_ready: list[str] = []

        for task in batch:
            processed.add(task)

            for dependent in dependents[task]:
                remaining_prerequisites[dependent].discard(task)
                if not remaining_prerequisites[dependent]:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if len(processed) != len(all_tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches
