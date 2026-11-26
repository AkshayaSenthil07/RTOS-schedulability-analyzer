
from engine.tasks import Task
from engine.event_simulation import simulate_events


def test_single_task_completes():
    tasks = [Task("T1", 2, 5, 0)]

    result = simulate_events(tasks, 5)

    assert result["jobs"][0]["completion_time"] == 2


def test_higher_priority_task_preempts():
    tasks = [
        Task("T1", 2, 5, 0),
        Task("T2", 4, 8, 1)
    ]

    result = simulate_events(tasks, 9)

    t2_job = next(
        job for job in result["jobs"]
        if job["task"] == "T2" and job["job_id"] == 1
    )

    assert t2_job["completion_time"] == 8

    assert len(result["preemptions"]) == 1
    assert result["preemptions"][0]["time"] == 5


def test_idle_time_is_recorded():
    tasks = [Task("T1", 1, 5, 0)]

    result = simulate_events(tasks, 3)

    assert result["intervals"] == [
        {
            "start": 0,
            "end": 1,
            "task": "T1",
            "job_id": 1,
            "kind": "execution"
        },
        {
            "start": 1,
            "end": 3,
            "task": None,
            "job_id": None,
            "kind": "idle"
        }
    ]


def test_simulation_rejects_empty_tasks():
    import pytest

    with pytest.raises(ValueError):
        simulate_events([], 10)


def test_simulation_rejects_invalid_duration():
    import pytest

    tasks = [Task("T1", 1, 5, 0)]

    with pytest.raises(ValueError):
        simulate_events(tasks, 0)


def test_simulation_rejects_duplicate_names():
    import pytest

    tasks = [
        Task("T1", 1, 5, 0),
        Task("T1", 2, 8, 1)
    ]

    with pytest.raises(ValueError):
        simulate_events(tasks, 10)


def test_large_duration_does_not_create_per_microsecond_trace():
    tasks = [Task("T1", 1, 1_000_000, 0)]

    result = simulate_events(tasks, 1_000_000)

    assert len(result["intervals"]) == 2
    assert result["intervals"][0]["end"] == 1
    assert result["intervals"][1]["kind"] == "idle"


def test_job_completion_and_release_at_same_time():
    tasks = [
        Task("T1", 1, 4, 1),
        Task("T2", 1, 2, 0)
    ]

    result = simulate_events(tasks, 4)

    t1_job = next(
        job for job in result["jobs"]
        if job["task"] == "T1" and job["job_id"] == 1
    )

    t2_second_job = next(
        job for job in result["jobs"]
        if job["task"] == "T2" and job["job_id"] == 2
    )

    assert t1_job["completion_time"] == 2
    assert t2_second_job["release_time"] == 2

    assert result["intervals"][2] == {
        "start": 2,
        "end": 3,
        "task": "T2",
        "job_id": 2,
        "kind": "execution"
    }
