from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Plan tasks into parallelizable batches based on their dependencies.

    Each key in ``dependencies`` is a task, and its value is the list of tasks
    that must be completed before it. Tasks that appear only as dependencies are
    included. Each returned batch is sorted alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle.
    """
    nodes: Set[str] = set(dependencies)
    for prereqs in dependencies.values():
        nodes.update(prereqs)

    dependents: Dict[str, Set[str]] = defaultdict(set)
    indegree: Dict[str, int] = {node: 0 for node in nodes}

    for task, prereqs in dependencies.items():
        for prereq in set(prereqs):
            dependents[prereq].add(task)
            indegree[task] += 1

    ready = sorted(node for node in nodes if indegree[node] == 0)
    batches: list[list[str]] = []
    processed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        processed_count += len(batch)

        next_ready: list[str] = []
        for completed in batch:
            for dependent in dependents[completed]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if processed_count != len(nodes):
        raise ValueError("Dependency graph contains a cycle")

    return batches
