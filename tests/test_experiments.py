
from engine.experiments import run_randomized_experiment


def test_experiment_runs_requested_number_of_sets():
    report = run_randomized_experiment(
        sets_per_level=2,
        num_tasks=3,
        seed=42
    )

    assert report["total_sets"] == 10


def test_experiment_accounts_for_every_task_set():
    report = run_randomized_experiment(
        sets_per_level=2,
        num_tasks=3,
        seed=42
    )

    assert (
        report["passed_sets"] + report["failed_sets"]
        == report["total_sets"]
    )

    assert (
        report["schedulable_sets"] + report["unschedulable_sets"]
        == report["total_sets"]
    )


def test_experiment_is_reproducible():
    first = run_randomized_experiment(
        sets_per_level=2,
        num_tasks=3,
        seed=42
    )

    second = run_randomized_experiment(
        sets_per_level=2,
        num_tasks=3,
        seed=42
    )

    assert first["passed_sets"] == second["passed_sets"]
    assert first["failed_sets"] == second["failed_sets"]
