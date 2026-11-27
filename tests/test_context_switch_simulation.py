
from engine.tasks import Task
from engine.overhead import SchedulerOverhead
from engine.event_simulation import simulate_events


def test_initial_dispatch_delays_first_execution():
    tasks = [
        Task("T1", 3, 10, 0, 10)
    ]

    overhead = SchedulerOverhead(
        initial_dispatch=2,
        context_switch=1
    )

    result = simulate_events(
        tasks,
        duration=8,
        overhead=overhead
    )

    execution = [
        interval for interval in result["intervals"]
        if interval["kind"] == "execution"
    ]

    dispatch = [
        interval for interval in result["intervals"]
        if interval["kind"] == "initial_dispatch"
    ]

    assert len(dispatch) == 1
    assert dispatch[0]["start"] == 0
    assert dispatch[0]["end"] == 2

    assert len(execution) == 1
    assert execution[0]["start"] == 2
    assert execution[0]["end"] == 5

    assert result["jobs"][0]["completion_time"] == 5



def test_context_switch_overhead_delays_preempting_task():
    tasks = [
        Task("T1", 5, 20, 1, 20),
        Task("T2", 2, 5, 0, 5)
    ]

    overhead = SchedulerOverhead(
        initial_dispatch=0,
        context_switch=1
    )

    result = simulate_events(
        tasks,
        duration=10,
        overhead=overhead
    )

    switches = [
        interval for interval in result["intervals"]
        if interval["kind"] == "context_switch"
    ]

    # First switch: T2 completes, then T1 starts.
    assert switches[0]["start"] == 2
    assert switches[0]["end"] == 3

    # Second switch: T2 preempts T1 at time 5.
    preemption_switch = next(
        interval for interval in switches
        if interval["start"] == 5
    )

    assert preemption_switch["end"] == 6

    t2_execution = [
        interval for interval in result["intervals"]
        if interval["task"] == "T2"
        and interval["kind"] == "execution"
        and interval["start"] >= 5
    ]

    assert t2_execution[0]["start"] == 6
