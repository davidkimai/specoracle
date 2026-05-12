"""
Module for planning task execution batches based on dependencies.
"""


def _prepare_graph_data(
    dependencies: dict[str, list[str]],
) -> tuple[set[str], dict[str, list[str]], dict[str, int]]:
    """
    Builds internal graph representations from the dependency dictionary.

    This helper function scans the dependency definition, validates its
    structure, and creates data structures suitable for topological sorting.

    Args:
        dependencies: A dictionary mapping a task to its prerequisites.

    Returns:
        A tuple containing:
        - all_tasks: A set of all unique task names.
        - successors: A dict mapping a task to tasks that depend on it.
        - in_degrees: A dict mapping a task to its prerequisite count.

    Raises:
        TypeError: If the input or its contents have an invalid type.
    """
    if not isinstance(dependencies, dict):
        raise TypeError("Dependencies must be a dictionary.")

    all_tasks = set(dependencies.keys())
    for task, prereq_list in dependencies.items():
        if not isinstance(task, str):
            raise TypeError(f"Task name {task!r} must be a string.")
        if not isinstance(prereq_list, list):
            raise TypeError(f"Prerequisites for task '{task}' must be a list.")
        for prereq in prereq_list:
            if not isinstance(prereq, str):
                raise TypeError(
                    f"Prerequisite '{prereq}' for task '{task}' must be a string."
                )
            all_tasks.add(prereq)

    successors = {task: [] for task in all_tasks}
    in_degrees = {task: 0 for task in all_tasks}

    for task, prereqs in dependencies.items():
        in_degrees[task] = len(prereqs)
        for prereq in prereqs:
            successors[prereq].append(task)

    return all_tasks, successors, in_degrees


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Calculates parallelizable batches of tasks from a dependency graph.

    This function performs a topological sort of the task graph to determine
    the order of execution. It groups tasks that have no outstanding
    dependencies into batches that can be run concurrently.

    Args:
        dependencies: A dictionary mapping a task name to a list of its
                      prerequisite task names. Tasks that only appear as
                      prerequisites are also included.

    Returns:
        A list of batches, where each batch is a list of task names that can
        be executed in parallel. Batches are ordered chronologically, and
        tasks within each batch are sorted alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle, making it
                    impossible to determine a valid execution order.
        TypeError: If the input `dependencies` object or its contents do
                   not match the expected types (e.g., not a dict, keys
                   are not strings, values are not lists of strings).
    """
    all_tasks, successors, remaining_in_degrees = _prepare_graph_data(dependencies)
    num_tasks = len(all_tasks)
    processed_tasks_count = 0
    batches = []

    while True:
        # Find all tasks with no remaining prerequisites.
        ready_tasks = sorted([
            task for task, degree in remaining_in_degrees.items() if degree == 0
        ])

        if not ready_tasks:
            # If no tasks are ready to run, we are done or have a cycle.
            break

        batches.append(ready_tasks)

        for task in ready_tasks:
            processed_tasks_count += 1
            # For each task that depends on the now-completed task,
            # decrement its prerequisite count.
            for successor_task in successors[task]:
                remaining_in_degrees[successor_task] -= 1
            # Remove the completed task from consideration.
            del remaining_in_degrees[task]

    if processed_tasks_count != num_tasks:
        # If the number of processed tasks is less than the total,
        # it implies a cycle prevented some tasks from ever becoming ready.
        raise ValueError("Dependency graph contains a cycle.")

    return batches
