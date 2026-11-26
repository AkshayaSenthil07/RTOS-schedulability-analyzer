
from engine.tasks import Task
from engine.jobs import Job
from engine.scheduler import select_next_job
from engine.events import next_event_time


def simulate_events(
    tasks: list[Task],
    duration: int
) -> dict:
    """
    Event-driven preemptive fixed-priority simulation.

    All time values are in microseconds (µs).

    This version does not yet model context-switch overhead
    or mutex blocking.
    """

    if not tasks:
        raise ValueError("At least one task is required")

    if duration <= 0:
        raise ValueError("Duration must be positive")

    if len({task.name for task in tasks}) != len(tasks):
        raise ValueError("Task names must be unique")

    ready_jobs = []
    all_jobs = []

    job_counters = {task.name: 0 for task in tasks}

    intervals = []
    preemptions = []

    current_time = 0
    previous_running_job = None

    while current_time < duration:

        # 1. Release jobs at the current time.
        for task in tasks:

            if current_time % task.T == 0:

                job_counters[task.name] += 1

                new_job = Job(
                    task=task,
                    job_id=job_counters[task.name],
                    release_time=current_time
                )

                ready_jobs.append(new_job)
                all_jobs.append(new_job)

        # 2. Select the highest-priority ready job.
        running_job = select_next_job(ready_jobs)

        # 3. Detect preemption.
        if (
            previous_running_job is not None
            and not previous_running_job.is_completed
            and running_job is not previous_running_job
        ):
            preemptions.append({
                "time": current_time,
                "preempted_task": previous_running_job.task.name,
                "preempted_job_id": previous_running_job.job_id,
                "by_task": (
                    running_job.task.name
                    if running_job is not None else None
                )
            })

        # 4. Find the next event.
        next_event = next_event_time(
            tasks,
            current_time,
            running_job
        )

        # The simulation must not go beyond its duration.
        next_time = min(next_event, duration)

        elapsed_time = next_time - current_time

        if elapsed_time <= 0:
            raise RuntimeError("Simulation failed to advance time")

        # 5. Execute the selected job for the elapsed time.
        if running_job is not None:

            running_job.remaining_execution -= elapsed_time

            if running_job.remaining_execution < 0:
                raise RuntimeError("Job execution became negative")

            # Record or extend an execution interval.
            if (
                intervals
                and intervals[-1]["task"] == running_job.task.name
                and intervals[-1]["job_id"] == running_job.job_id
                and intervals[-1]["end"] == current_time
            ):
                intervals[-1]["end"] = next_time

            else:
                intervals.append({
                    "start": current_time,
                    "end": next_time,
                    "task": running_job.task.name,
                    "job_id": running_job.job_id,
                    "kind": "execution"
                })

            # Record completion.
            if running_job.is_completed:
                running_job.completion_time = next_time

        else:
            # Record idle interval.
            if (
                intervals
                and intervals[-1]["kind"] == "idle"
                and intervals[-1]["end"] == current_time
            ):
                intervals[-1]["end"] = next_time

            else:
                intervals.append({
                    "start": current_time,
                    "end": next_time,
                    "task": None,
                    "job_id": None,
                    "kind": "idle"
                })

        previous_running_job = running_job

        # 6. Advance directly to the next event.
        current_time = next_time

    # 7. Analyze job completion and deadlines.
    results = []

    for job in all_jobs:

        missed_deadline = (
            job.completion_time is None
            and duration >= job.absolute_deadline
        ) or (
            job.completion_time is not None
            and job.completion_time > job.absolute_deadline
        )

        results.append({
            "task": job.task.name,
            "job_id": job.job_id,
            "release_time": job.release_time,
            "deadline": job.absolute_deadline,
            "completion_time": job.completion_time,
            "remaining_execution": job.remaining_execution,
            "deadline_missed": missed_deadline
        })

    return {
        "intervals": intervals,
        "preemptions": preemptions,
        "jobs": results
    }
