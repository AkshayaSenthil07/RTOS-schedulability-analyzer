
import math

from engine.tasks import Task


def hyperperiod(
    tasks: list[Task],
    max_ticks: int = 100_000
) -> int:
    """
    Calculate the least common multiple of all task periods.

    max_ticks prevents an impractically large simulation horizon.
    """

    if not tasks:
        raise ValueError("At least one task is required")

    if max_ticks <= 0:
        raise ValueError("max_ticks must be positive")

    result = 1

    for task in tasks:
        result = math.lcm(result, task.T)

        if result > max_ticks:
            raise ValueError(
                f"Hyperperiod exceeds the limit of {max_ticks} ticks"
            )

    return result


def releases_at(tasks: list[Task], t: int) -> list[Task]:
    """
    Return all tasks that release a new job at time t.

    Assumption: all periodic tasks have their first release at t = 0.
    """

    if not isinstance(t, int) or t < 0:
        raise ValueError("Time t must be a non-negative integer")

    return [
        task for task in tasks
        if t % task.T == 0
    ]
