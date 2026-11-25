
from engine.tasks import Task


def utilization(tasks: list[Task]) -> float:
    """
    Calculate total CPU utilization of periodic tasks.
    """
    return sum(task.C / task.T for task in tasks)


def rm_bound(n: int) -> float:
    """
    Calculate the classical Rate Monotonic
    sufficient utilization bound.
    """
    if n <= 0:
        raise ValueError("Number of tasks must be positive")

    return n * (2 ** (1 / n) - 1)


def utilization_test(tasks: list[Task]) -> str:
    """
    Return:
    guaranteed  - RM sufficient bound is satisfied
    inconclusive - bound cannot prove schedulability
    overloaded  - average execution demand exceeds CPU capacity

    Assumptions for the RM guarantee:
    single processor, preemptive fixed-priority RM,
    implicit deadlines (D = T), and no runtime overhead.
    """

    if not tasks:
        return "guaranteed"

    u = utilization(tasks)

    if u > 1:
        return "overloaded"

    # Classical RM bound assumes D = T
    if any(task.D != task.T for task in tasks):
        return "inconclusive"

    bound = rm_bound(len(tasks))

    if u <= bound:
        return "guaranteed"

    return "inconclusive"
