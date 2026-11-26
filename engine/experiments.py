
from engine.task_generation import generate_task_set
from engine.validation import validate_task_set
from engine.utilization import utilization


def run_randomized_experiment(
    sets_per_level: int = 100,
    num_tasks: int = 5,
    seed: int = 42
) -> dict:

    utilization_levels = [0.30, 0.50, 0.70, 0.90, 1.00]

    report = {
        "total_sets": 0,
        "passed_sets": 0,
        "failed_sets": 0,
        "schedulable_sets": 0,
        "unschedulable_sets": 0,
        "disagreements": [],
        "levels": []
    }

    for level_index, target in enumerate(utilization_levels):

        level_report = {
            "target_utilization": target,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "schedulable": 0,
            "unschedulable": 0,
            "actual_utilizations": []
        }

        for case_index in range(sets_per_level):

            case_seed = seed + level_index * sets_per_level + case_index

            tasks = generate_task_set(
                num_tasks=num_tasks,
                total_utilization=target,
                seed=case_seed
            )

            actual_u = utilization(tasks)

            result = validate_task_set(tasks)

            report["total_sets"] += 1
            level_report["total"] += 1

            level_report["actual_utilizations"].append(actual_u)

            if result["passed"]:
                report["passed_sets"] += 1
                level_report["passed"] += 1
            else:
                report["failed_sets"] += 1
                level_report["failed"] += 1

                report["disagreements"].append({
                    "seed": case_seed,
                    "target_utilization": target,
                    "actual_utilization": actual_u,
                    "tasks": tasks,
                    "details": result["disagreements"]
                })

            if all(
                item["schedulable"]
                for item in result["rta_results"].values()
            ):
                report["schedulable_sets"] += 1
                level_report["schedulable"] += 1
            else:
                report["unschedulable_sets"] += 1
                level_report["unschedulable"] += 1

        report["levels"].append(level_report)

    return report
