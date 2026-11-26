
import pytest

from engine.tasks import Task
from engine.rta import response_time_analysis


def test_rta_sample_task_set():
    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 2, 6, 1),
        Task("T3", 3, 12, 2)
    ]

    results = response_time_analysis(tasks)

    assert results["T1"]["response_time"] == 1
    assert results["T2"]["response_time"] == 3
    assert results["T3"]["response_time"] == 10

    assert all(
        result["schedulable"]
        for result in results.values()
    )


def test_rta_unschedulable_task():
    tasks = [
        Task("T1", 2, 4, 0),
        Task("T2", 3, 6, 1)
    ]

    results = response_time_analysis(tasks)

    assert results["T1"]["schedulable"]
    assert not results["T2"]["schedulable"]
    assert results["T2"]["response_time"] > 6


def test_rta_single_task():
    tasks = [
        Task("T1", 2, 10, 0)
    ]

    results = response_time_analysis(tasks)

    assert results["T1"]["response_time"] == 2
    assert results["T1"]["schedulable"]


def test_rta_rejects_empty_task_list():
    with pytest.raises(ValueError):
        response_time_analysis([])


def test_rta_rejects_duplicate_priorities():
    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 1, 6, 0)
    ]

    with pytest.raises(ValueError):
        response_time_analysis(tasks)


def test_rta_with_custom_deadline():
    tasks = [
        Task("T1", 2, 10, 0, 5)
    ]

    results = response_time_analysis(tasks)

    assert results["T1"]["response_time"] == 2
    assert results["T1"]["schedulable"]
