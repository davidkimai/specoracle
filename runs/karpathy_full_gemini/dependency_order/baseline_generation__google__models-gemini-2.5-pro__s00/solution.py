"""
Provides a function to determine the execution order of tasks with dependencies.
"""

import collections


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Calculates a parallel execution plan for a set of tasks with dependencies.

    The function performs a topological sort of the dependency graph and groups
    tasks into batches that can be executed in parallel.

    Args:
        dependencies: A dictionary mapping a task name to a list of its
                      dependencies. Tasks that only appear as dependencies
                      (i.e., in the lists) but not as keys are considered
                      to have no dependencies themselves.

    Returns:
        A list of batches (lists of task names). Each inner list contains
        tasks that can be run in parallel and is sorted alphabetically.
        The outer list represents the sequence of batches.

    Raises:
        ValueError: If the dependency graph contains a cycle, making it
                    impossible to create a valid execution plan.
    """
    # Build the graph representation: an adjacency list for dependents
    # and a count of incoming edges (in-degrees) for each task.
    adj_list = collections.defaultdict(list)
    in_degree = collections.defaultdict(int)

    all_tasks = set(dependencies.keys())
    for deps in dependencies.values():
        all_tasks.update(deps)

    for task, deps in dependencies.items():
        for dep in deps:
            # Create an edge from the dependency to the task.
            adj_list[dep].append(task)
            in_degree[task] += 1

    # Initialize the first batch with tasks that have no dependencies.
    queue = [task for task in all_tasks if in_degree[task] == 0]

    batches = []
    processed_count = 0

    # Process tasks in batches using Kahn's algorithm for topological sorting.
    while queue:
        # The current queue contains all tasks that can be run in this batch.
        # Sort alphabetically as required.
        current_batch = sorted(queue)
        batches.append(current_batch)
        processed_count += len(current_batch)

        # Prepare the next batch by finding tasks whose dependencies are now met.
        next_queue = []
        for task in current_batch:
            for dependent_task in adj_list[task]:
                in_degree[dependent_task] -= 1
                if in_degree[dependent_task] == 0:
                    next_queue.append(dependent_task)

        queue = next_queue

    # If the number of processed tasks is less than the total number of tasks,
    # the graph has a cycle.
    if processed_count != len(all_tasks):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
