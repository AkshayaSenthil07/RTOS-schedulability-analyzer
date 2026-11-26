
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    """
    Represents a periodic real-time task.

    All timing values are expressed in microseconds (µs).

    Attributes:
        name: Task identifier.
        C: Worst-case execution time (µs).
        T: Task period (µs).
        priority: Task priority (lower number = higher priority).
        D: Relative deadline (µs). Defaults to T.
    """

    name: str
    C: int
    T: int
    priority: int
    D: int | None = None

    def __post_init__(self):

        if self.C <= 0:
            raise ValueError("Execution time C must be positive")

        if self.T <= 0:
            raise ValueError("Period T must be positive")

        if self.priority < 0:
            raise ValueError("Priority cannot be negative")

        if self.D is None:
            object.__setattr__(self, "D", self.T)

        if self.D <= 0:
            raise ValueError("Deadline D must be positive")
