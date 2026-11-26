import pytest

from engine.tasks import Task
from engine.jobs import Job


def test_job_initializes_with_full_execution_time():
    task = Task("T1", 2, 5, 0)

    job = Job(task, 1, 0)

    assert job.remaining_execution == 2


def test_job_calculates_absolute_deadline():
    task = Task("T1", 2, 5, 0)

    job = Job(task, 1, 3)

    assert job.absolute_deadline == 8


def test_job_is_not_completed_initially():
    task = Task("T1", 2, 5, 0)

    job = Job(task, 1, 0)

    assert not job.is_completed


def test_job_is_completed_when_execution_reaches_zero():
    task = Task("T1", 2, 5, 0)

    job = Job(task, 1, 0)
    job.remaining_execution = 0

    assert job.is_completed


def test_job_rejects_non_positive_id():
    task = Task("T1", 2, 5, 0)

    with pytest.raises(ValueError):
        Job(task, 0, 0)


def test_job_rejects_negative_release_time():
    task = Task("T1", 2, 5, 0)

    with pytest.raises(ValueError):
        Job(task, 1, -1)