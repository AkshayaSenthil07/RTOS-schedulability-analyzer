
import math
import random


def generate_utilizations(
    num_tasks: int,
    total_utilization: float,
    seed: int | None = None
) -> list[float]:
    """
    Generate task utilizations using the UUniFast algorithm.

    Assumptions:
    - Number of tasks must be positive.
    - Total utilization must be greater than 0 and at most 1.
    - A fixed seed makes the results reproducible.
    """

    if (
        not isinstance(num_tasks, int)
        or isinstance(num_tasks, bool)
        or num_tasks <= 0
    ):
        raise ValueError("Number of tasks must be a positive integer")

    if (
        isinstance(total_utilization, bool)
        or not isinstance(total_utilization, (int, float))
        or not math.isfinite(total_utilization)
        or not 0 < total_utilization <= 1
    ):
        raise ValueError(
            "Total utilization must be greater than 0 and at most 1"
        )

    rng = random.Random(seed)

    utilizations = []
    remaining_utilization = float(total_utilization)

    for i in range(1, num_tasks):

        next_remaining = (
            remaining_utilization
            * rng.random() ** (1 / (num_tasks - i))
        )

        current_utilization = (
            remaining_utilization - next_remaining
        )

        utilizations.append(current_utilization)
        remaining_utilization = next_remaining

    utilizations.append(remaining_utilization)

    return utilizations


from engine.tasks import Task


def generate_task_set(
    num_tasks: int,
    total_utilization: float,
    seed: int | None = None,
    min_period: int = 10,
    max_period: int = 100
) -> list[Task]:
    """
    Generate independent periodic tasks using UUniFast.

    Periods are integer microseconds.
    Deadlines are implicit (D = T).
    Lower numerical priority means higher priority.
    """

    if (
        not isinstance(min_period, int)
        or isinstance(min_period, bool)
        or not isinstance(max_period, int)
        or isinstance(max_period, bool)
        or min_period <= 0
        or max_period < min_period
    ):
        raise ValueError("Invalid period range")

    utilizations = generate_utilizations(
        num_tasks,
        total_utilization,
        seed
    )

    rng = random.Random(seed)

    tasks = []

    for i, task_utilization in enumerate(utilizations):

        period = rng.randint(min_period, max_period)

        execution = max(
            1,
            round(task_utilization * period)
        )

        # Keep execution time within the task period.
        execution = min(execution, period)

        task = Task(
            name=f"T{i + 1}",
            C=execution,
            T=period,
            D=period,
            priority=i
        )

        tasks.append(task)

    return tasks

