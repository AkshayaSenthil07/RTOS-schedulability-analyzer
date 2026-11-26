from engine.tasks import Task
from engine.jobs import Job
from engine.scheduler import select_next_job


def test_selects_highest_priority_job():
    t1 = Task("T1", 2, 5, 0)
    t2 = Task("T2", 3, 10, 1)

    jobs = [
        Job(t2, 1, 0),
        Job(t1, 1, 0)
    ]

    selected = select_next_job(jobs)

    assert selected.task.name == "T1"


def test_selects_only_available_job():
    task = Task("T1", 2, 5, 0)
    job = Job(task, 1, 0)

    assert select_next_job([job]) == job


def test_ignores_completed_jobs():
    t1 = Task("T1", 2, 5, 0)
    t2 = Task("T2", 3, 10, 1)

    high_priority_job = Job(t1, 1, 0)
    high_priority_job.remaining_execution = 0

    lower_priority_job = Job(t2, 1, 0)

    selected = select_next_job([
        high_priority_job,
        lower_priority_job
    ])

    assert selected == lower_priority_job


def test_returns_none_when_no_jobs_are_ready():
    assert select_next_job([]) is None


def test_returns_none_when_all_jobs_are_completed():
    task = Task("T1", 2, 5, 0)
    job = Job(task, 1, 0)
    job.remaining_execution = 0

    assert select_next_job([job]) is None


def test_priority_wins_over_release_time():
    t1 = Task("T1", 2, 5, 0)
    t2 = Task("T2", 3, 10, 1)

    jobs = [
        Job(t2, 1, 0),
        Job(t1, 1, 2)
    ]

    selected = select_next_job(jobs)

    assert selected.task.name == "T1"