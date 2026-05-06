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
    been satisfied by previous batches.  Raises ValueError if the
    dependency graph contains a cycle.

    If *completed* is provided, those tasks are treated as already
    finished: they are excluded from the returned batches but their
    edges are honoured when computing readiness of remaining tasks.
    """
    graph = _build_graph(dependencies)
    done = set(completed) if completed else set()
    return _kahn_batches(graph, done)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a canonical adjacency map that includes every node that
    appears either as a key or as a dependency value.
    """
    graph: dict[str, list[str]] = {}

    for task, prereqs in dependencies.items():
        if task not in graph:
            graph[task] = []
        for prereq in prereqs:
            graph[task].append(prereq)
            if prereq not in graph:
                graph[prereq] = []

    return graph


def _in_degrees(graph: dict[str, list[str]], done: set[str]) -> dict[str, int]:
    """
    Compute in-degree for every node, treating *done* tasks as already
    satisfied (their contribution to in-degree is zero).
    """
    return {
        task: sum(1 for prereq in prereqs if prereq not in done)
        for task, prereqs in graph.items()
    }


def _reverse_edges(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Build a reverse adjacency map: for each prereq, list the tasks
    that directly depend on it.
    """
    reverse: dict[str, list[str]] = {task: [] for task in graph}
    for task, prereqs in graph.items():
        for prereq in prereqs:
            reverse[prereq].append(task)
    return reverse


def _kahn_batches(graph: dict[str, list[str]], done: set[str]) -> list[list[str]]:
    """
    Run Kahn's algorithm, collecting nodes into parallel batches.
    Tasks in *done* are skipped in output but their edges are pre-satisfied.
    """
    in_deg = _in_degrees(graph, done)
    dependents = _reverse_edges(graph)

    # Nodes that are already done start as "processed" without emitting a batch.
    # Remaining nodes with in-degree 0 are the initial ready set.
    ready = deque(
        task for task, deg in in_deg.items()
        if deg == 0 and task not in done
    )
    batches: list[list[str]] = []

    # Count nodes we need to process (excluding pre-completed ones).
    remaining = {task for task in graph if task not in done}
    processed = 0

    while ready:
        batch = sorted(ready)
        batches.append(batch)
        ready.clear()

        for task in batch:
            processed += 1
            for dependent in dependents[task]:
                if dependent in done:
                    continue
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    ready.append(dependent)

    if processed != len(remaining):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
