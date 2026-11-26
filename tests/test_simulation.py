import pytest

from engine.tasks import Task
from engine.simulation import simulate


def test_simulation_releases_jobs():
    tasks = [Task("T1", 1, 3, 0)]

    result = simulate(tasks, 7)

    assert len(result["jobs"]) == 3


def test_simulation_executes_job():
    tasks = [Task("T1", 2, 5, 0)]

    result = simulate(tasks, 5)

    assert result["jobs"][0]["completion_time"] == 2


def test_simulation_respects_priority():
    tasks = [
        Task("T1", 2, 5, 0),
        Task("T2", 2, 5, 1)
    ]

    result = simulate(tasks, 4)

    executed_tasks = [
        entry["task"] for entry in result["timeline"]
    ]

    assert executed_tasks[:2] == ["T1", "T1"]
    assert executed_tasks[2:] == ["T2", "T2"]


def test_simulation_records_idle_time():
    tasks = [Task("T1", 1, 5, 0)]

    result = simulate(tasks, 3)

    assert len(result["timeline"]) == 1


def test_simulation_rejects_empty_tasks():
    with pytest.raises(ValueError):
        simulate([], 10)


def test_simulation_rejects_invalid_duration():
    tasks = [Task("T1", 1, 5, 0)]

    with pytest.raises(ValueError):
        simulate(tasks, 0)

def test_higher_priority_job_preempts_lower_priority_job():
    tasks = [
        Task("T1", 2, 5, 0),
        Task("T2", 4, 8, 1)
    ]

    result = simulate(tasks, 9)

    executed_tasks = [
        entry["task"] for entry in result["timeline"]
    ]

    assert executed_tasks == [
        "T1", "T1",
        "T2", "T2", "T2",
        "T1", "T1",
        "T2", "T2"
    ]


def test_trace_records_every_tick_including_idle():
    tasks = [Task("T1", 1, 5, 0)]

    result = simulate(tasks, 3)

    assert len(result["trace"]) == 3
    assert result["trace"][0]["task"] == "T1"
    assert result["trace"][1]["task"] is None
    assert result["trace"][2]["task"] is None


def test_intervals_group_consecutive_execution():
    tasks = [Task("T1", 2, 5, 0)]

    result = simulate(tasks, 3)

    assert result["intervals"] == [
        {
            "start": 0,
            "end": 2,
            "task": "T1",
            "job_id": 1,
            "kind": "execution"
        },
        {
            "start": 2,
            "end": 3,
            "task": None,
            "job_id": None,
            "kind": "idle"
        }
    ]


def test_preemption_is_recorded():
    tasks = [
        Task("T1", 2, 5, 0),
        Task("T2", 4, 8, 1)
    ]

    result = simulate(tasks, 9)

    assert len(result["preemptions"]) == 1

    event = result["preemptions"][0]

    assert event["time"] == 5
    assert event["preempted_task"] == "T2"
    assert event["by_task"] == "T1"


def test_preempted_job_resumes_with_remaining_execution():
    tasks = [
        Task("T1", 2, 5, 0),
        Task("T2", 5, 8, 1)
    ]

    result = simulate(tasks, 9)

    t2_job = next(
        job for job in result["jobs"]
        if job["task"] == "T2"
    )

    assert t2_job["remaining_execution"] == 0
    assert t2_job["completion_time"] == 9


def test_simulation_rejects_duplicate_task_names():
    tasks = [
        Task("T1", 1, 5, 0),
        Task("T1", 2, 8, 1)
    ]

    with pytest.raises(ValueError):
        simulate(tasks, 10)

def test_unfinished_job_is_marked_missed_at_deadline():
    tasks = [
        Task("T1", 3, 10, 0, 2)
    ]

    result = simulate(tasks, 2)

    job = result["jobs"][0]

    assert job["completion_time"] is None
    assert job["remaining_execution"] == 1
    assert job["deadline_missed"]


def test_completion_exactly_at_deadline_is_on_time():
    tasks = [
        Task("T1", 2, 10, 0, 2)
    ]

    result = simulate(tasks, 2)

    job = result["jobs"][0]

    assert job["completion_time"] == 2
    assert not job["deadline_missed"]

