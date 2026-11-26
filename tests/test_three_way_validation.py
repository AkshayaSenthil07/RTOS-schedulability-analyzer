
from engine.tasks import Task
from engine.rta import response_time_analysis
from engine.simulation import simulate
from engine.event_simulation import simulate_events


def test_rta_tick_and_event_simulators_agree():

    # 1. Define the same task set for all three implementations.
    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 2, 7, 1),
        Task("T3", 3, 12, 2)
    ]

    duration = 30

    # 2. Run analytical response-time analysis.
    rta_results = response_time_analysis(tasks)

    # 3. Run both simulators with zero overhead.
    tick_results = simulate(tasks, duration)
    event_results = simulate_events(tasks, duration)

    # 4. Expected analytical response times.
    expected = {
        "T1": 1,
        "T2": 3,
        "T3": 7
    }

    for task_name, expected_response in expected.items():

        # Check RTA against the known answer.
        assert rta_results[task_name]["response_time"] == expected_response

        # Find the first job in the tick simulator.
        tick_job = next(
            job for job in tick_results["jobs"]
            if job["task"] == task_name and job["job_id"] == 1
        )

        # Find the first job in the event-driven simulator.
        event_job = next(
            job for job in event_results["jobs"]
            if job["task"] == task_name and job["job_id"] == 1
        )

        # Both first jobs must complete.
        assert tick_job["completion_time"] is not None
        assert event_job["completion_time"] is not None

        # Calculate their observed response times.
        tick_response = (
            tick_job["completion_time"] - tick_job["release_time"]
        )

        event_response = (
            event_job["completion_time"] - event_job["release_time"]
        )

        # All three implementations must agree.
        assert tick_response == expected_response
        assert event_response == expected_response

        # The first jobs must meet their deadlines.
        assert tick_job["deadline_missed"] is False
        assert event_job["deadline_missed"] is False
