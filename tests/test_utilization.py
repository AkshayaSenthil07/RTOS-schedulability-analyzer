
import pytest

from engine.tasks import Task
from engine.utilization import (
    utilization,
    rm_bound,
    utilization_test
)


def test_utilization_calculation():
    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 2, 6, 1),
        Task("T3", 3, 12, 2)
    ]

    assert utilization(tasks) == pytest.approx(0.8333333)


def test_rm_bound_for_three_tasks():
    assert rm_bound(3) == pytest.approx(0.7798, abs=0.0001)


def test_rm_guaranteed():
    tasks = [
        Task("T1", 1, 10, 0),
        Task("T2", 1, 10, 1)
    ]

    assert utilization_test(tasks) == "guaranteed"


def test_overloaded():
    tasks = [
        Task("T1", 3, 4, 0),
        Task("T2", 3, 4, 1)
    ]

    assert utilization_test(tasks) == "overloaded"


def test_rm_inconclusive():
    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 2, 6, 1),
        Task("T3", 3, 12, 2)
    ]

    assert utilization_test(tasks) == "inconclusive"


def test_rm_bound_rejects_zero_tasks():
    with pytest.raises(ValueError):
        rm_bound(0)
