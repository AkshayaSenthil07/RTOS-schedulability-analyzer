
from engine.tasks import Task
from engine.rta import response_time_analysis
from engine.simulation import simulate
from engine.event_simulation import simulate_events


def validate_task_set(tasks: list[Task]) -> dict:
    """
    Cross-check one synchronous task set using:
    1. Response-time analysis
    2. Tick-based simulation
    3. Event-driven simulation

    Assumptions:
    - Single-core preemptive fixed-priority scheduling
    - Unique priorities
    - Independent periodic tasks
    - Synchronous releases at time zero
    - Zero scheduling overhead
    - Implicit deadlines (D = T)
    """

    if not tasks:
        raise ValueError("At least one task is required")

    if any(task.D != task.T for task in tasks):
        raise ValueError(
            "This validation currently requires implicit deadlines (D = T)"
        )

    # Run the analytical calculation.
    rta_results = response_time_analysis(tasks)

    # Simulate long enough for every first job's deadline to pass.
    duration = max(task.D for task in tasks) + 1

    tick_results = simulate(tasks, duration)
    event_results = simulate_events(tasks, duration)

    disagreements = []

    for task in tasks:

        task_name = task.name

        expected_schedulable = rta_results[task_name]["schedulable"]
        expected_response = rta_results[task_name]["response_time"]

        tick_job = next(
            (
                job for job in tick_results["jobs"]
                if job["task"] == task_name and job["job_id"] == 1
            ),
            None
        )

        event_job = next(
            (
                job for job in event_results["jobs"]
                if job["task"] == task_name and job["job_id"] == 1
            ),
            None
        )

        if tick_job is None or event_job is None:
            disagreements.append({
                "task": task_name,
                "problem": "First job missing from a simulator"
            })
            continue

        # Check the tick simulator's deadline verdict.
        tick_schedulable = not tick_job["deadline_missed"]

        if tick_schedulable != expected_schedulable:
            disagreements.append({
                "task": task_name,
                "implementation": "tick",
                "rta_schedulable": expected_schedulable,
                "simulation_schedulable": tick_schedulable
            })

        # Check the event simulator's deadline verdict.
        event_schedulable = not event_job["deadline_missed"]

        if event_schedulable != expected_schedulable:
            disagreements.append({
                "task": task_name,
                "implementation": "event",
                "rta_schedulable": expected_schedulable,
                "simulation_schedulable": event_schedulable
            })

        # For schedulable jobs, compare exact response times.
        if expected_schedulable:

            tick_response = (
                tick_job["completion_time"] - tick_job["release_time"]
                if tick_job["completion_time"] is not None
                else None
            )

            event_response = (
                event_job["completion_time"] - event_job["release_time"]
                if event_job["completion_time"] is not None
                else None
            )

            if tick_response != expected_response:
                disagreements.append({
                    "task": task_name,
                    "implementation": "tick",
                    "rta_response": expected_response,
                    "simulation_response": tick_response
                })

            if event_response != expected_response:
                disagreements.append({
                    "task": task_name,
                    "implementation": "event",
                    "rta_response": expected_response,
                    "simulation_response": event_response
                })

    return {
        "total_tasks": len(tasks),
        "rta_results": rta_results,
        "disagreements": disagreements,
        "passed": len(disagreements) == 0
    }
