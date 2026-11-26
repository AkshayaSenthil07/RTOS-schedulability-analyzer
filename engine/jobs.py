
from dataclasses import dataclass, field

from engine.tasks import Task


@dataclass
class Job:
    """
    Represents one released instance of a periodic task.

    All time values are expressed in microseconds (µs).
    """

    task: Task
    job_id: int
    release_time: int

    remaining_execution: int = field(init=False)
    completion_time: int | None = None

    def __post_init__(self):

        if not isinstance(self.job_id, int) or isinstance(self.job_id, bool):
            raise ValueError("Job ID must be an integer")

        if self.job_id <= 0:
            raise ValueError("Job ID must be positive")

        if not isinstance(self.release_time, int) or isinstance(self.release_time, bool):
            raise ValueError("Release time must be an integer")

        if self.release_time < 0:
            raise ValueError("Release time cannot be negative")

        self.remaining_execution = self.task.C

    @property
    def absolute_deadline(self) -> int:
        return self.release_time + self.task.D

    @property
    def is_completed(self) -> bool:
        return self.remaining_execution == 0
