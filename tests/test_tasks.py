
import pytest

from engine.tasks import Task


def test_default_deadline():
    task = Task("T1", 1, 5, 0)

    assert task.D == 5


def test_custom_deadline():
    task = Task("T1", 2, 10, 0, 8)

    assert task.D == 8


def test_execution_time_must_be_positive():
    with pytest.raises(ValueError):
        Task("T1", 0, 5, 0)


def test_period_must_be_positive():
    with pytest.raises(ValueError):
        Task("T1", 1, 0, 0)


def test_priority_must_be_non_negative():
    with pytest.raises(ValueError):
        Task("T1", 1, 5, -1)
