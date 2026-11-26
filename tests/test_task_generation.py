
import pytest

from engine.task_generation import generate_utilizations


def test_generated_utilizations_sum_to_target():
    values = generate_utilizations(5, 0.75, seed=42)

    assert sum(values) == pytest.approx(0.75)


def test_each_utilization_is_between_zero_and_one():
    values = generate_utilizations(10, 0.90, seed=42)

    assert all(0 <= value <= 1 for value in values)


def test_same_seed_produces_same_results():
    first = generate_utilizations(5, 0.75, seed=42)
    second = generate_utilizations(5, 0.75, seed=42)

    assert first == second


def test_different_seeds_produce_different_results():
    first = generate_utilizations(5, 0.75, seed=42)
    second = generate_utilizations(5, 0.75, seed=99)

    assert first != second


def test_single_task_receives_all_utilization():
    values = generate_utilizations(1, 0.60, seed=42)

    assert values == [0.60]


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        generate_utilizations(0, 0.75)

    with pytest.raises(ValueError):
        generate_utilizations(5, 0)

    with pytest.raises(ValueError):
        generate_utilizations(5, 1.5)


from engine.task_generation import generate_task_set


def test_task_set_generation_returns_requested_number():
    tasks = generate_task_set(5, 0.75, seed=42)

    assert len(tasks) == 5


def test_generated_tasks_have_valid_parameters():
    tasks = generate_task_set(5, 0.75, seed=42)

    for task in tasks:
        assert task.C > 0
        assert task.T > 0
        assert task.C <= task.T
        assert task.D == task.T


def test_task_set_generation_is_reproducible():
    first = generate_task_set(5, 0.75, seed=42)
    second = generate_task_set(5, 0.75, seed=42)

    assert first == second


def test_generated_task_priorities_are_unique():
    tasks = generate_task_set(5, 0.75, seed=42)

    priorities = [task.priority for task in tasks]

    assert len(priorities) == len(set(priorities))


def test_invalid_period_range_is_rejected():
    with pytest.raises(ValueError):
        generate_task_set(5, 0.75, min_period=100, max_period=10)
