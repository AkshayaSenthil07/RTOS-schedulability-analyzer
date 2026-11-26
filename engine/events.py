
from engine.tasks import Task


def next_release_time(
    tasks: list[Task],
    current_time: int
) -> int | None:
    """
    Return the earliest task release strictly after current_time.

    All time values are in microseconds (µs).
    """

    if not isinstance(current_time, int) or isinstance(current_time, bool):
        raise ValueError("Current time must be an integer")

    if current_time < 0:
        raise ValueError("Current time cannot be negative")

    if not tasks:
        return None

    future_releases = []

    for task in tasks:
        next_release = (
            (current_time // task.T) + 1
        ) * task.T

        future_releases.append(next_release)

    return min(future_releases)


from engine.jobs import Job


def next_event_time(
    tasks: list[Task],
    current_time: int,
    running_job: Job | None = None
) -> int | None:
    """
    Find the next release or running-job completion event.

    All time values are in microseconds (µs).
    """

    next_release = next_release_time(tasks, current_time)

    possible_events = []

    if next_release is not None:
        possible_events.append(next_release)

    if running_job is not None and not running_job.is_completed:
        completion_time = (
            current_time + running_job.remaining_execution
        )
        possible_events.append(completion_time)

    if not possible_events:
        return None

    return min(possible_events)
