
from dataclasses import dataclass


@dataclass(frozen=True)
class SchedulerOverhead:
    """
    Represents scheduling overhead.

    All timing values are expressed in microseconds (µs).
    """

    initial_dispatch: int = 0
    context_switch: int = 0

    def __post_init__(self):

        if (
            not isinstance(self.initial_dispatch, int)
            or isinstance(self.initial_dispatch, bool)
        ):
            raise ValueError(
                "Initial dispatch cost must be an integer"
            )

        if (
            not isinstance(self.context_switch, int)
            or isinstance(self.context_switch, bool)
        ):
            raise ValueError(
                "Context-switch cost must be an integer"
            )

        if self.initial_dispatch < 0:
            raise ValueError(
                "Initial dispatch cost cannot be negative"
            )

        if self.context_switch < 0:
            raise ValueError(
                "Context-switch cost cannot be negative"
            )
