
def diagnose_deadline_misses(simulation_result: dict) -> list[dict]:
    """
    Generate explanations for jobs that missed their deadlines.

    Uses actual execution intervals and preemption records
    from the event-driven simulator.
    """

    intervals = simulation_result["intervals"]
    preemptions = simulation_result["preemptions"]
    jobs = simulation_result["jobs"]

    diagnoses = []

    for job in jobs:

        if not job["deadline_missed"]:
            continue

        task_name = job["task"]
        job_id = job["job_id"]

        # Find execution intervals belonging to this exact job.
        job_intervals = [
            interval for interval in intervals
            if interval["task"] == task_name
            and interval["job_id"] == job_id
            and interval["kind"] == "execution"
        ]

        # Calculate how much CPU execution the job received.
        executed_time = sum(
            interval["end"] - interval["start"]
            for interval in job_intervals
        )

        # Find preemptions experienced by this exact job.
        job_preemptions = [
            event for event in preemptions
            if event["preempted_task"] == task_name
            and event["preempted_job_id"] == job_id
        ]

        preempted_by = sorted({
            event["by_task"]
            for event in job_preemptions
            if event["by_task"] is not None
        })

        completion_time = job["completion_time"]

        if completion_time is None:
            status = "incomplete_at_simulation_end"
            lateness = None

            explanation = (
                f"The job did not complete by its deadline. "
                f"It received {executed_time} µs of CPU execution "
                f"and has {job['remaining_execution']} µs remaining."
            )

        else:
            status = "completed_late"
            lateness = completion_time - job["deadline"]

            explanation = (
                f"The job completed at {completion_time} µs, "
                f"which is {lateness} µs after its deadline."
            )

        if preempted_by:
            explanation += (
                f" It was preempted {len(job_preemptions)} times "
                f"by higher-priority task(s): "
                f"{', '.join(preempted_by)}."
            )

        diagnoses.append({
            "task": task_name,
            "job_id": job_id,
            "deadline": job["deadline"],
            "completion_time": completion_time,
            "status": status,
            "executed_time": executed_time,
            "remaining_execution": job["remaining_execution"],
            "lateness": lateness,
            "preemption_count": len(job_preemptions),
            "preempted_by": preempted_by,
            "explanation": explanation
        })

    return diagnoses
