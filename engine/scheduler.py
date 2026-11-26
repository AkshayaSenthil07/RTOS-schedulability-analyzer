from engine.jobs import Job


def select_next_job(ready_jobs: list[Job]) -> Job | None:
    """
    Select the highest-priority ready job.

    Lower numerical priority means higher priority.
    Completed jobs are ignored.
    """

    available_jobs = [
        job for job in ready_jobs
        if not job.is_completed
    ]

    if not available_jobs:
        return None

    return min(
        available_jobs,
        key=lambda job: (job.task.priority, job.release_time, job.job_id)
    )