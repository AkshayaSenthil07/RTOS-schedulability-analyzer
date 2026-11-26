
import pytest

from engine.tasks import Task
from engine.event_simulation import simulate_events
from engine.gantt import generate_gantt_svg


def test_gantt_svg_is_created(tmp_path):

    tasks = [
        Task("T1", 2, 5, 0),
        Task("T2", 2, 10, 1)
    ]

    duration = 15

    result = simulate_events(tasks, duration)

    output = tmp_path / "gantt.svg"

    generate_gantt_svg(
        result,
        str(output),
        duration
    )

    assert output.exists()

    content = output.read_text(encoding="utf-8")

    assert "<svg" in content
    assert "CPU Execution Gantt Chart" in content


def test_gantt_rejects_invalid_duration(tmp_path):

    with pytest.raises(ValueError):

        generate_gantt_svg(
            {"intervals": [{"start": 0, "end": 1,
                            "task": "T1", "job_id": 1,
                            "kind": "execution"}]},
            str(tmp_path / "gantt.svg"),
            0
        )


def test_gantt_rejects_invalid_intervals(tmp_path):

    result = {
        "intervals": [
            {
                "start": 5,
                "end": 2,
                "task": "T1",
                "job_id": 1,
                "kind": "execution"
            }
        ]
    }

    with pytest.raises(ValueError):

        generate_gantt_svg(
            result,
            str(tmp_path / "gantt.svg"),
            10
        )

def test_gantt_displays_preemption_marker(tmp_path):

    tasks = [
        Task("T1", 1, 4, 0),
        Task("T2", 4, 10, 1)
    ]

    duration = 12

    result = simulate_events(tasks, duration)

    assert len(result["preemptions"]) >= 1

    output = tmp_path / "preemption.svg"

    generate_gantt_svg(
        result,
        str(output),
        duration
    )

    content = output.read_text(encoding="utf-8")

    assert "Preemption" in content
    assert 'stroke-dasharray="4,3"' in content