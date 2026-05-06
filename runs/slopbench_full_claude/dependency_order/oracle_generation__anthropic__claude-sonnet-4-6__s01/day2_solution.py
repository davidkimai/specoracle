"""
dependency_order.py

Topological batch scheduler using Kahn's algorithm.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose prerequisites have all
    been satisfied by previous batches. Tasks that only appear as
    dependencies (not as keys) are included automatically.

    If *completed* is provided, those tasks are treated as already
    finished: they are excluded from every returned batch but still
    count as satisfying dependencies for remaining tasks.

    Raises ValueError if the dependency graph contains a cycle.
    """
    graph = _build_graph(dependencies)
    return _kahn_batches(graph, completed=completed or set())


def _build_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a complete adjacency map (task -> prerequisites) that includes
    every node mentioned anywhere in the input, without mutating the input.
    """
    graph: dict[str, list[str]] = {}

    for task, prereqs in dependencies.items():
        graph.setdefault(task, [])
        for prereq in prereqs:
            graph[task] = list(graph[task])  # already a copy below
            graph.setdefault(prereq, [])

    # Build clean copies so we never touch the caller's lists.
    return {task: list(prereqs) for task, prereqs in dependencies.items()} | {
        node: [] for node in graph if node not in dependencies
    }


def _in_degree_and_dependents(
    graph: dict[str, list[str]],
) -> tuple[dict[str, int], dict[str, list[str]]]:
    """
    Compute in-degree (number of prerequisites) for every node and
    a reverse map (prereq -> tasks that depend on it).
    """
    in_degree: dict[str, int] = {node: 0 for node in graph}
    dependents: dict[str, list[str]] = {node: [] for node in graph}

    for task, prereqs in graph.items():
        in_degree[task] = len(prereqs)
        for prereq in prereqs:
            dependents[prereq].append(task)

    return in_degree, dependents


def _kahn_batches(
    graph: dict[str, list[str]],
    *,
    completed: set[str],
) -> list[list[str]]:
    """
    Execute Kahn's algorithm, collecting nodes into parallel batches.
    Each batch contains all nodes whose in-degree reached zero together.

    Nodes in *completed* are pre-processed (their dependents get their
    in-degree decremented) but are never placed into a batch.
    """
    in_degree, dependents = _in_degree_and_dependents(graph)

    # Pre-process completed tasks: decrement dependents' in-degrees as if
    # those tasks had already run, then remove them from consideration.
    for task in completed:
        if task in graph:
            for dependent in dependents[task]:
                in_degree[dependent] -= 1
            # Mark as processed by removing from in_degree tracking.
            del in_degree[task]

    ready = deque(sorted(node for node, deg in in_degree.items() if deg == 0))
    batches: list[list[str]] = []
    processed = len(completed & graph.keys())  # count pre-processed nodes

    while ready:
        batch = sorted(ready)
        batches.append(batch)
        ready.clear()

        for task in batch:
            processed += 1
            for dependent in dependents[task]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    ready.append(dependent)

        ready = deque(sorted(ready))

    if processed != len(graph):
        raise ValueError(
            "Cycle detected in the dependency graph; topological ordering is impossible."
        )

    return batches
