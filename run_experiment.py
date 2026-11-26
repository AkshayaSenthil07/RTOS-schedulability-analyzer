
from engine.experiments import run_randomized_experiment


report = run_randomized_experiment(
    sets_per_level=100,
    num_tasks=5,
    seed=42
)

print("\n===== RANDOMIZED VALIDATION REPORT =====")

print("Total task sets:", report["total_sets"])
print("Passed:", report["passed_sets"])
print("Failed:", report["failed_sets"])
print("Schedulable:", report["schedulable_sets"])
print("Unschedulable:", report["unschedulable_sets"])

print("\n===== UTILIZATION LEVELS =====")

for level in report["levels"]:
    print(
        f"Target U={level['target_utilization']:.2f} | "
        f"Passed={level['passed']} | "
        f"Failed={level['failed']} | "
        f"Schedulable={level['schedulable']} | "
        f"Unschedulable={level['unschedulable']}"
    )

if report["disagreements"]:
    print("\n===== FIRST DISAGREEMENT =====")
    print(report["disagreements"][0])
else:
    print("\nNo disagreements found.")
