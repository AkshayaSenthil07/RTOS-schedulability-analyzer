
from engine.tasks import Task
from engine.jobs import Job
from engine.scheduler import select_next_job


def simulate(
    tasks: list[Task],
    duration: int
) -> dict:

    if not tasks:
        raise ValueError("At least one task is required")

    if duration <= 0:
        raise ValueError("Duration must be positive")

    if len({task.name for task in tasks}) != len(tasks):
        raise ValueError("Task names must be unique")

    ready_jobs = []
    all_jobs = []

    # Existing timeline: records only CPU execution.
    timeline = []

    # New trace: records every tick, including idle time.
    trace = []

    preemptions = []

    job_counters = {task.name: 0 for task in tasks}
    previous_running_job = None

    for current_time in range(duration):

        # 1. Release new jobs
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

        # 2. Select the highest-priority ready job
        running_job = select_next_job(ready_jobs)

        # 3. Detect preemption
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

        # 4. Execute or record idle time
        if running_job is not None:

            running_job.remaining_execution -= 1

            entry = {
                "time": current_time,
                "task": running_job.task.name,
                "job_id": running_job.job_id
            }

            timeline.append(entry)
            trace.append(entry.copy())

            # Record completion time
            if running_job.is_completed:
                running_job.completion_time = current_time + 1

        else:
            trace.append({
                "time": current_time,
                "task": None,
                "job_id": None
            })

        previous_running_job = running_job

    # 5. Group consecutive ticks into intervals
    intervals = []

    for entry in trace:

        key = (entry["task"], entry["job_id"])

        if (
            not intervals
            or (
                intervals[-1]["task"],
                intervals[-1]["job_id"]
            ) != key
        ):
            intervals.append({
                "start": entry["time"],
                "end": entry["time"] + 1,
                "task": entry["task"],
                "job_id": entry["job_id"],
                "kind": (
                    "execution"
                    if entry["task"] is not None
                    else "idle"
                )
            })
        else:
            intervals[-1]["end"] = entry["time"] + 1

    # 6. Analyze job completion and deadline status
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
        "timeline": timeline,
        "trace": trace,
        "intervals": intervals,
        "preemptions": preemptions,
        "jobs": results
    }
