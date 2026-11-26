
import argparse

from engine.input_loader import load_tasks_from_json
from engine.rta import response_time_analysis
from engine.event_simulation import simulate_events
from engine.gantt import generate_gantt_svg
from engine.utilization import utilization
from engine.diagnostics import diagnose_deadline_misses

def main():

    parser = argparse.ArgumentParser(
        description="FreeRTOS Schedulability Analyzer"
    )

    parser.add_argument(
        "input",
        help="Path to the JSON task input file"
    )

    parser.add_argument(
        "--output",
        default="gantt.svg",
        help="Output SVG Gantt chart filename"
    )

    args = parser.parse_args()

    # 1. Load user-defined tasks.
    tasks, duration = load_tasks_from_json(args.input)

    # 2. Calculate total utilization.
    total_utilization = utilization(tasks)

    # 3. Perform analytical response-time analysis.
    rta_results = response_time_analysis(tasks)

    # 4. Perform event-driven simulation.
    simulation = simulate_events(tasks, duration)
    diagnoses = diagnose_deadline_misses(simulation)
    # 5. Generate the Gantt chart.
    generate_gantt_svg(
        simulation,
        args.output,
        duration
    )

    # 6. Display the analysis report.
    print("\n===== FREERTOS SCHEDULABILITY ANALYZER =====")

    print(f"Input file: {args.input}")
    print(f"Number of tasks: {len(tasks)}")
    print(f"Simulation duration: {duration} µs")
    print(f"Total utilization: {total_utilization:.3f}")

    print("\n===== TASK ANALYSIS =====")

    for task in sorted(tasks, key=lambda item: item.priority):

        result = rta_results[task.name]

        print(f"\nTask: {task.name}")
        print(f"  Execution time: {task.C} µs")
        print(f"  Period: {task.T} µs")
        print(f"  Deadline: {task.D} µs")
        print(f"  Priority: {task.priority}")
        print(f"  RTA response time: {result['response_time']} µs")
        print(
            f"  RTA verdict: "
            f"{'SCHEDULABLE' if result['schedulable'] else 'UNSCHEDULABLE'}"
        )

    # 7. Display the overall verdict.
    all_schedulable = all(
        result["schedulable"]
        for result in rta_results.values()
    )

    print("\n===== OVERALL RESULT =====")

    if all_schedulable:
        print("All tasks are schedulable according to RTA.")
    else:
        print("At least one task is not schedulable according to RTA.")

    print("\n===== SIMULATION =====")

    missed_jobs = [
        job for job in simulation["jobs"]
        if job["deadline_missed"]
    ]

    print(f"Jobs simulated: {len(simulation['jobs'])}")
    print(f"Deadline misses observed: {len(missed_jobs)}")

    for job in missed_jobs:
        print(
            f"  {job['task']} Job {job['job_id']} "
            f"missed deadline at {job['deadline']} µs"
        )

    if diagnoses:
        print("\n===== DEADLINE MISS DIAGNOSIS =====")

        for diagnosis in diagnoses:
            print("\n------------------------------")
            print(f"Task: {diagnosis['task']}")
            print(f"Job: {diagnosis['job_id']}")
            print(f"Deadline: {diagnosis['deadline']} µs")
            print(f"Status: {diagnosis['status']}")
            print(f"Execution received: {diagnosis['executed_time']} µs")

            if diagnosis["completion_time"] is not None:
                print(
                    f"Completion time: "
                    f"{diagnosis['completion_time']} µs"
                )
                print(f"Lateness: {diagnosis['lateness']} µs")
            else:
                print(
                    f"Remaining execution: "
                    f"{diagnosis['remaining_execution']} µs"
                )

            print(
                f"Preemptions: {diagnosis['preemption_count']}"
            )
            print(
                f"Preempted by: {diagnosis['preempted_by']}"
            )
            print(f"Explanation: {diagnosis['explanation']}")

    print(f"\nGantt chart saved to: {args.output}")


if __name__ == "__main__":
    main()
