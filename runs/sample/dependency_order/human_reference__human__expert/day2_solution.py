from __future__ import annotations


def plan_batches(
    dependencies: dict[str, list[str]], completed: set[str] | None = None
) -> list[list[str]]:
    done = set() if completed is None else set(completed)

    tasks = set(dependencies)
    for blockers in dependencies.values():
        tasks.update(blockers)
    tasks -= done

    remaining = {task: set(dependencies.get(task, [])) - done for task in tasks}
    batches: list[list[str]] = []
    while remaining:
        ready = sorted(task for task, blockers in remaining.items() if not blockers)
        if not ready:
            raise ValueError("dependency graph contains a cycle")

        batches.append(ready)
        completed_batch = set(ready)
        remaining = {
            task: blockers - completed_batch
            for task, blockers in remaining.items()
            if task not in completed_batch
        }
    return batches
