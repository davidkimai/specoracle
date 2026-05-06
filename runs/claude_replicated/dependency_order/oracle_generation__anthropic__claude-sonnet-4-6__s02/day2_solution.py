"""
dependency_order.py

Topological batch scheduler: groups tasks into parallel waves respecting
dependency order.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of task names whose dependencies were all
    satisfied by previous batches.  Raises ValueError if the dependency
    graph contains a cycle.

    Parameters
    ----------
    dependencies:
        Mapping from task name to the list of tasks that must finish first.
    completed:
        Optional set of task names already finished.  These tasks are omitted
        from the returned batches but still count as satisfied prerequisites
        for remaining tasks.

    Returns
    -------
    list[list[str]]
        Ordered list of batches; tasks within each batch are alphabetically
        sorted.
    """
    done: set[str] = set(completed) if completed else set()
    graph, in_degree = _build_graph(dependencies, done)
    return _kahn_batches(graph, in_degree, done)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_tasks(dependencies: dict[str, list[str]]) -> set[str]:
    """Collect every task name that appears anywhere in the mapping."""
    names: set[str] = set(dependencies)
    for prereqs in dependencies.values():
        names.update(prereqs)
    return names


def _build_graph(
    dependencies: dict[str, list[str]],
    completed: set[str],
) -> tuple[dict[str, list[str]], dict[str, int]]:
    """
    Build an adjacency list (successor direction) and an in-degree counter
    for every known task.

    Completed tasks are excluded from the graph nodes but their outgoing
    edges are still used to reduce in-degrees of successors.

    Returns (graph, in_degree) where graph[a] lists tasks that depend on a.
    """
    tasks = _all_tasks(dependencies)

    # Only include non-completed tasks as graph nodes.
    remaining = tasks - completed

    graph: dict[str, list[str]] = {t: [] for t in remaining}
    in_degree: dict[str, int] = {t: 0 for t in remaining}

    for task, prereqs in dependencies.items():
        if task in completed:
            # Skip edges whose target is already done.
            continue
        for prereq in prereqs:
            if prereq in completed:
                # This prerequisite is already satisfied; don't add an edge.
                continue
            graph[prereq].append(task)
            in_degree[task] += 1

    return graph, in_degree


def _kahn_batches(
    graph: dict[str, list[str]],
    in_degree: dict[str, int],
    completed: set[str],
) -> list[list[str]]:
    """
    Kahn's algorithm extended to collect tasks level-by-level (batch-by-batch).

    Raises ValueError on cycle detection.
    """
    # Work on a mutable copy so the caller's data is untouched.
    degree = dict(in_degree)

    queue: deque[str] = deque(
        sorted(task for task, d in degree.items() if d == 0)
    )

    batches: list[list[str]] = []
    processed = 0
    total = len(degree)

    while queue:
        # Everything currently in the queue forms one parallel batch.
        batch_size = len(queue)
        batch = [queue.popleft() for _ in range(batch_size)]
        batches.append(sorted(batch))
        processed += len(batch)

        next_ready: list[str] = []
        for task in batch:
            for successor in graph[task]:
                degree[successor] -= 1
                if degree[successor] == 0:
                    next_ready.append(successor)

        queue.extend(sorted(next_ready))

    if processed != total:
        raise ValueError(
            "Dependency graph contains a cycle; topological ordering is impossible."
        )

    return batches
