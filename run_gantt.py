
from engine.tasks import Task
from engine.event_simulation import simulate_events
from engine.gantt import generate_gantt_svg


tasks = [
    Task("T1", 1, 4, 0),
    Task("T2", 4, 10, 1)
]

duration = 12

result = simulate_events(tasks, duration)

print("Preemptions:", result["preemptions"])

generate_gantt_svg(
    result,
    "preemption_gantt.svg",
    duration
)

print("Generated: preemption_gantt.svg")
