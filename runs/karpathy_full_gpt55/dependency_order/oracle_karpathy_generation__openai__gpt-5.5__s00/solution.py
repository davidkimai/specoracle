def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    remaining = {task: set(prereqs) for task, prereqs in dependencies.items()}

    for prereqs in dependencies.values():
        for prereq in prereqs:
            remaining.setdefault(prereq, set())

    batches = []

    while remaining:
        batch = sorted(task for task, prereqs in remaining.items() if not prereqs)
        if not batch:
            raise ValueError("dependency graph contains a cycle")

        batches.append(batch)

        completed = set(batch)
        for task in batch:
            del remaining[task]

        for prereqs in remaining.values():
            prereqs.difference_update(completed)

    return batches
