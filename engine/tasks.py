
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    name: str
    C: int
    T: int
    priority: int
    D: int | None = None

    def __post_init__(self):

        # Execution time must be positive
        if self.C <= 0:
            raise ValueError("Execution time C must be positive")

        # Period must be positive
        if self.T <= 0:
            raise ValueError("Period T must be positive")

        # Priority cannot be negative
        if self.priority < 0:
            raise ValueError("Priority cannot be negative")

        # Use the period as deadline if D is not provided
        if self.D is None:
            object.__setattr__(self, "D", self.T)

        # Deadline must be positive
        if self.D <= 0:
            raise ValueError("Deadline D must be positive")
