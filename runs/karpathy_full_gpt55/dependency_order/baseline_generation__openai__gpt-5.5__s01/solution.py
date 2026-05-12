from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    all_tasks: set[str] = set(dependencies)
    prerequisite_sets: dict[str, set[str]] = {}

    for task, prerequisites in dependencies.items():
        prereq_set = set(prerequisites)
        prerequisite_sets[task] = prereq_set
        all_tasks.update(prereq_set)

    adjacency: dict[str, set[str]] = {task: set() for task in all_tasks}
    indegree: dict[str, int] = {task: 0 for task in all_tasks}

    for task, prereq_set in prerequisite_sets.items():
        indegree[task] = len(prereq_set)
        for prerequisite in prereq_set:
            adjacency[prerequisite].add(task)

    batches: list[list[str]] = []
    ready = sorted(task for task, count in indegree.items() if count == 0)
    processed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        processed_count += len(batch)

        next_ready: list[str] = []
        for task in batch:
            for dependent in adjacency[task]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if processed_count != len(all_tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches
