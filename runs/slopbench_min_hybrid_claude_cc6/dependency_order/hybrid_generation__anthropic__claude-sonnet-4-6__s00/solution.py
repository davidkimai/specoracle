"""
dependency_order.py

Topological batch scheduler using Kahn's algorithm.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch contains tasks whose prerequisites have all been satisfied
    by previous batches. Tasks within a batch are sorted alphabetically.

    Raises ValueError if the dependency graph contains a cycle.
    """
    graph, in_degree = _build_graph(dependencies)
    return _kahn_batches(graph, in_degree)


def _collect_all_tasks(dependencies: dict[str, list[str]]) -> set[str]:
    """Return the union of all task names and all dependency names."""
    tasks = set(dependencies)
    for prereqs in dependencies.values():
        tasks.update(prereqs)
    return tasks


def _build_graph(
    dependencies: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, int]]:
    """
    Build an adjacency list and in-degree map from the dependency dict.

    Edge direction: prerequisite -> dependent (prereq must run first).
    """
    all_tasks = _collect_all_tasks(dependencies)
    graph: dict[str, list[str]] = {task: [] for task in all_tasks}
    in_degree: dict[str, int] = {task: 0 for task in all_tasks}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            graph[prereq].append(task)
            in_degree[task] += 1

    return graph, in_degree


def _initial_queue(in_degree: dict[str, int]) -> deque:
    """Return a deque of tasks with no prerequisites, sorted alphabetically."""
    return deque(sorted(task for task, deg in in_degree.items() if deg == 0))


def _drain_queue(queue: deque) -> list[str]:
    """Remove and return all current items from the queue as a sorted list."""
    batch = [queue.popleft() for _ in range(len(queue))]
    return sorted(batch)


def _ready_dependents(
    batch: list[str],
    graph: dict[str, list[str]],
    remaining: dict[str, int],
) -> list[str]:
    """Decrement in-degrees and return tasks that become ready after this batch."""
    newly_ready = []
    for task in batch:
        for dependent in graph[task]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                newly_ready.append(dependent)
    return sorted(newly_ready)


def _kahn_batches(
    graph: dict[str, list[str]],
    in_degree: dict[str, int],
) -> list[list[str]]:
    """
    Run Kahn's algorithm and group tasks into parallel batches.

    Raises ValueError if the graph contains a cycle.
    """
    remaining = dict(in_degree)
    queue = _initial_queue(remaining)
    batches: list[list[str]] = []
    processed = 0

    while queue:
        batch = _drain_queue(queue)
        batches.append(batch)
        processed += len(batch)
        queue.extend(_ready_dependents(batch, graph, remaining))

    if processed != len(graph):
        raise ValueError(
            "Dependency graph contains a cycle; topological ordering is impossible."
        )

    return batches
