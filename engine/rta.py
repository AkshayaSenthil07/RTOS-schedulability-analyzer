
from engine.tasks import Task


def response_time_analysis(
    tasks: list[Task]
) -> dict[str, dict[str, int | bool]]:
    """
    Classical fixed-priority response-time analysis.

    Assumptions:
    - Single processor
    - Preemptive fixed-priority scheduling
    - Unique task priorities
    - Independent periodic tasks
    - No mutex blocking
    - No context-switch or other runtime overhead

    Lower numerical priority value means higher priority.
    """

    if not tasks:
        raise ValueError("At least one task is required")

    priorities = [task.priority for task in tasks]

    if len(priorities) != len(set(priorities)):
        raise ValueError("Task priorities must be unique for this analysis")

    results = {}

    # Analyze tasks from highest priority to lowest priority
    ordered_tasks = sorted(tasks, key=lambda task: task.priority)

    for task in ordered_tasks:

        # Find all higher-priority tasks
        higher_priority_tasks = [
            other for other in ordered_tasks
            if other.priority < task.priority
        ]

        # Initial response-time estimate
        R = task.C

        while True:

            interference = sum(
                ((R + hp.T - 1) // hp.T) * hp.C
                for hp in higher_priority_tasks
            )

            new_R = task.C + interference

            # Fixed point reached
            if new_R == R:
                results[task.name] = {
                    "response_time": R,
                    "schedulable": R <= task.D
                }
                break

            # Response time has exceeded the deadline
            if new_R > task.D:
                results[task.name] = {
                    "response_time": new_R,
                    "schedulable": False
                }
                break

            R = new_R

    return results
