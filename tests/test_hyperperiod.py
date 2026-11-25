
import pytest

from engine.tasks import Task
from engine.hyperperiod import hyperperiod, releases_at


@pytest.fixture
def sample_tasks():
    return [
        Task("T1", 1, 4, 0),
        Task("T2", 2, 6, 1),
        Task("T3", 3, 12, 2)
    ]


def test_hyperperiod_calculation(sample_tasks):
    assert hyperperiod(sample_tasks) == 12


def test_hyperperiod_limit(sample_tasks):
    with pytest.raises(ValueError):
        hyperperiod(sample_tasks, max_ticks=10)


def test_empty_task_list():
    with pytest.raises(ValueError):
        hyperperiod([])


def test_zero_time_releases_all_tasks(sample_tasks):
    released = releases_at(sample_tasks, 0)

    assert [task.name for task in released] == ["T1", "T2", "T3"]


def test_release_at_six(sample_tasks):
    released = releases_at(sample_tasks, 6)

    assert [task.name for task in released] == ["T2"]


def test_release_at_four(sample_tasks):
    released = releases_at(sample_tasks, 4)

    assert [task.name for task in released] == ["T1"]


def test_negative_time_rejected(sample_tasks):
    with pytest.raises(ValueError):
        releases_at(sample_tasks, -1)
