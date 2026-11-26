
import pytest

from engine.tasks import Task
from engine.validation import validate_task_set


def test_known_task_set_passes_three_way_validation():
    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 2, 7, 1),
        Task("T3", 3, 12, 2)
    ]

    result = validate_task_set(tasks)

    assert result["passed"] is True
    assert result["disagreements"] == []


def test_unschedulable_task_set_is_detected():
    tasks = [
        Task("T1", 3, 5, 0),
        Task("T2", 4, 6, 1)
    ]

    result = validate_task_set(tasks)

    assert result["passed"] is True
    assert result["disagreements"] == []
    assert result["rta_results"]["T2"]["schedulable"] is False


def test_empty_task_set_is_rejected():
    with pytest.raises(ValueError):
        validate_task_set([])


def test_arbitrary_deadlines_are_rejected():
    tasks = [
        Task("T1", 2, 5, 0, D=4)
    ]

    with pytest.raises(ValueError):
        validate_task_set(tasks)
