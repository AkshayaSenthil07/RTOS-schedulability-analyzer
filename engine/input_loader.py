
import json

from pathlib import Path
from engine.tasks import Task


def load_tasks_from_json(file_path: str) -> tuple[list[Task], int]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Invalid JSON file") from error

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")

    if set(data) != {"duration", "tasks"}:
        raise ValueError(
            "JSON must contain exactly 'duration' and 'tasks'"
        )

    duration = data["duration"]

    if (
        not isinstance(duration, int)
        or isinstance(duration, bool)
        or duration <= 0
    ):
        raise ValueError("Duration must be a positive integer")

    task_data = data["tasks"]

    if not isinstance(task_data, list) or not task_data:
        raise ValueError("Tasks must be a non-empty list")

    tasks = []

    required_fields = {"name", "C", "T", "D", "priority"}

    for item in task_data:

        if not isinstance(item, dict):
            raise ValueError("Each task must be a JSON object")

        if set(item) != required_fields:
            raise ValueError(
                f"Each task must contain: {sorted(required_fields)}"
            )

        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ValueError("Task name must be a non-empty string")

        for field in ("C", "T", "D", "priority"):
            value = item[field]

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise ValueError(f"{field} must be an integer")

        tasks.append(Task(**item))

    if len({task.name for task in tasks}) != len(tasks):
        raise ValueError("Task names must be unique")

    if len({task.priority for task in tasks}) != len(tasks):
        raise ValueError("Task priorities must be unique")

    return tasks, duration
