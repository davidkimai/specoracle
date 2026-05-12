from __future__ import annotations


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    already_done = set(completed) if completed else set()

    tasks = set(dependencies)
    for blockers in dependencies.values():
        tasks.update(blockers)

    remaining = {
        task: set(dependencies.get(task, [])) - already_done
        for task in tasks
        if task not in already_done
    }
    batches: list[list[str]] = []
    while remaining:
        ready = sorted(task for task, blockers in remaining.items() if not blockers)
        if not ready:
            raise ValueError("dependency graph contains a cycle")

        batches.append(ready)
        completed_now = set(ready)
        remaining = {
            task: blockers - completed_now
            for task, blockers in remaining.items()
            if task not in completed_now
        }
    return batches
