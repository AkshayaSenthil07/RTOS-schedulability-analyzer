
import pytest

from engine.tasks import Task
from engine.events import next_release_time


def test_next_release_time():
    tasks = [
        Task("T1", 100, 1000, 0),
        Task("T2", 200, 2500, 1),
        Task("T3", 300, 4000, 2)
    ]

    assert next_release_time(tasks, 1200) == 2000


def test_next_release_at_time_zero():
    tasks = [Task("T1", 100, 1000, 0)]

    assert next_release_time(tasks, 0) == 1000


def test_release_time_moves_to_next_period():
    tasks = [Task("T1", 100, 1000, 0)]

    assert next_release_time(tasks, 2000) == 3000


def test_empty_tasks_return_none():
    assert next_release_time([], 100) is None


def test_negative_time_is_rejected():
    tasks = [Task("T1", 100, 1000, 0)]

    with pytest.raises(ValueError):
        next_release_time(tasks, -1)


def test_non_integer_time_is_rejected():
    tasks = [Task("T1", 100, 1000, 0)]

    with pytest.raises(ValueError):
        next_release_time(tasks, 1.5)


from engine.jobs import Job
from engine.events import next_event_time


def test_completion_happens_before_next_release():
    tasks = [Task("T1", 100, 1000, 0)]
    job = Job(tasks[0], 1, 0)
    job.remaining_execution = 300

    assert next_event_time(tasks, 1200, job) == 1500


def test_release_happens_before_completion():
    tasks = [Task("T1", 100, 1000, 0)]
    job = Job(tasks[0], 1, 0)
    job.remaining_execution = 1500

    assert next_event_time(tasks, 1200, job) == 2000


def test_no_running_job_returns_next_release():
    tasks = [Task("T1", 100, 1000, 0)]

    assert next_event_time(tasks, 1200) == 2000


def test_completed_job_is_not_a_future_event():
    tasks = [Task("T1", 100, 1000, 0)]
    job = Job(tasks[0], 1, 0)
    job.remaining_execution = 0

    assert next_event_time(tasks, 1200, job) == 2000
