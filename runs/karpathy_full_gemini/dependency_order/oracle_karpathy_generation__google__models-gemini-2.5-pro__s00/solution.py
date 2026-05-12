import collections
from typing import Dict, List, Set

def plan_batches(dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """
    Calculates an execution plan for a set of tasks with dependencies.

    The plan is a list of batches, where each batch is a list of tasks that
    can be run in parallel. Tasks within each batch are sorted alphabetically.
    This function performs a topological sort of the dependency graph.

    Args:
        dependencies: A dictionary mapping a task name to a list of its
                      prerequisites. Tasks that only appear as prerequisites
                      (i.e., in the lists of values) are also included.

    Returns:
        A list of lists of task names, representing the execution plan.

    Raises:
        ValueError: If the dependency graph contains a cycle, making it
                    impossible to create a valid execution plan.
    """
    # Identify all unique tasks and build graph representations.
    # `adj_list`: prerequisite -> [tasks that depend on it]
    # `in_degree`: task -> number of prerequisites
    all_tasks: Set[str] = set(dependencies.keys())
    for prereq_list in dependencies.values():
        all_tasks.update(prereq_list)

    adj_list: Dict[str, List[str]] = collections.defaultdict(list)
    in_degree: Dict[str, int] = {task: 0 for task in all_tasks}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            adj_list[prereq].append(task)
            in_degree[task] += 1

    # Initialize the first batch with tasks that have no prerequisites.
    queue = [task for task in all_tasks if in_degree[task] == 0]

    batches: List[List[str]] = []
    processed_tasks_count = 0

    # Process tasks in batches (Kahn's algorithm).
    while queue:
        # Sort the current batch alphabetically for deterministic output.
        current_batch = sorted(queue)
        batches.append(current_batch)
        processed_tasks_count += len(current_batch)

        next_queue: List[str] = []
        for task in current_batch:
            # For each completed task, update its dependents.
            for dependent in adj_list[task]:
                in_degree[dependent] -= 1
                # If a dependent has no more prerequisites, add it to the next batch.
                if in_degree[dependent] == 0:
                    next_queue.append(dependent)

        queue = next_queue

    # If not all tasks were processed, the graph has a cycle.
    if processed_tasks_count != len(all_tasks):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
