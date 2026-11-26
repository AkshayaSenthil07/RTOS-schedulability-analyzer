
from engine.diagnostics import diagnose_deadline_misses


def test_completed_late_job():
    result = {
        "intervals": [
            {
                "start": 0,
                "end": 3,
                "task": "T2",
                "job_id": 1,
                "kind": "execution"
            },
            {
                "start": 5,
                "end": 7,
                "task": "T2",
                "job_id": 1,
                "kind": "execution"
            }
        ],
        "preemptions": [
            {
                "time": 3,
                "preempted_task": "T2",
                "preempted_job_id": 1,
                "by_task": "T1"
            }
        ],
        "jobs": [
            {
                "task": "T2",
                "job_id": 1,
                "deadline": 6,
                "completion_time": 7,
                "remaining_execution": 0,
                "deadline_missed": True
            }
        ]
    }

    diagnoses = diagnose_deadline_misses(result)

    assert len(diagnoses) == 1
    assert diagnoses[0]["status"] == "completed_late"
    assert diagnoses[0]["lateness"] == 1
    assert diagnoses[0]["executed_time"] == 5
    assert diagnoses[0]["preemption_count"] == 1
    assert diagnoses[0]["preempted_by"] == ["T1"]


def test_incomplete_job():
    result = {
        "intervals": [
            {
                "start": 0,
                "end": 3,
                "task": "T2",
                "job_id": 1,
                "kind": "execution"
            }
        ],
        "preemptions": [],
        "jobs": [
            {
                "task": "T2",
                "job_id": 1,
                "deadline": 5,
                "completion_time": None,
                "remaining_execution": 2,
                "deadline_missed": True
            }
        ]
    }

    diagnoses = diagnose_deadline_misses(result)

    assert len(diagnoses) == 1
    assert diagnoses[0]["status"] == "incomplete_at_simulation_end"
    assert diagnoses[0]["completion_time"] is None
    assert diagnoses[0]["executed_time"] == 3
    assert diagnoses[0]["remaining_execution"] == 2
    assert diagnoses[0]["lateness"] is None


def test_missed_job_without_preemption():
    result = {
        "intervals": [
            {
                "start": 0,
                "end": 6,
                "task": "T1",
                "job_id": 1,
                "kind": "execution"
            }
        ],
        "preemptions": [],
        "jobs": [
            {
                "task": "T1",
                "job_id": 1,
                "deadline": 5,
                "completion_time": 6,
                "remaining_execution": 0,
                "deadline_missed": True
            }
        ]
    }

    diagnoses = diagnose_deadline_misses(result)

    assert len(diagnoses) == 1
    assert diagnoses[0]["status"] == "completed_late"
    assert diagnoses[0]["preemption_count"] == 0
    assert diagnoses[0]["preempted_by"] == []


def test_no_deadline_misses():
    result = {
        "intervals": [],
        "preemptions": [],
        "jobs": [
            {
                "task": "T1",
                "job_id": 1,
                "deadline": 5,
                "completion_time": 3,
                "remaining_execution": 0,
                "deadline_missed": False
            }
        ]
    }

    diagnoses = diagnose_deadline_misses(result)

    assert diagnoses == []
