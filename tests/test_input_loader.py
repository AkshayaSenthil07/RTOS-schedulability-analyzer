
import json
import pytest

from engine.input_loader import load_tasks_from_json


def test_load_valid_json(tmp_path):

    data = {
        "duration": 30,
        "tasks": [
            {
                "name": "T1",
                "C": 2,
                "T": 5,
                "D": 5,
                "priority": 0
            }
        ]
    }

    file = tmp_path / "tasks.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    tasks, duration = load_tasks_from_json(str(file))

    assert len(tasks) == 1
    assert tasks[0].name == "T1"
    assert duration == 30


def test_missing_file_is_rejected(tmp_path):

    with pytest.raises(FileNotFoundError):
        load_tasks_from_json(str(tmp_path / "missing.json"))


def test_invalid_json_is_rejected(tmp_path):

    file = tmp_path / "invalid.json"
    file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(ValueError):
        load_tasks_from_json(str(file))


def test_negative_execution_time_is_rejected(tmp_path):

    data = {
        "duration": 30,
        "tasks": [
            {
                "name": "T1",
                "C": -2,
                "T": 5,
                "D": 5,
                "priority": 0
            }
        ]
    }

    file = tmp_path / "tasks.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_tasks_from_json(str(file))


def test_duplicate_priorities_are_rejected(tmp_path):

    data = {
        "duration": 30,
        "tasks": [
            {
                "name": "T1",
                "C": 2,
                "T": 5,
                "D": 5,
                "priority": 0
            },
            {
                "name": "T2",
                "C": 3,
                "T": 10,
                "D": 10,
                "priority": 0
            }
        ]
    }

    file = tmp_path / "tasks.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_tasks_from_json(str(file))
