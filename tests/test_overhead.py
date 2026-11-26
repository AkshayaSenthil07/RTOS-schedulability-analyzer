
import pytest

from engine.overhead import SchedulerOverhead


def test_valid_overhead_configuration():

    overhead = SchedulerOverhead(
        initial_dispatch=100,
        context_switch=50
    )

    assert overhead.initial_dispatch == 100
    assert overhead.context_switch == 50


def test_zero_overhead_is_allowed():

    overhead = SchedulerOverhead(
        initial_dispatch=0,
        context_switch=0
    )

    assert overhead.initial_dispatch == 0
    assert overhead.context_switch == 0


def test_negative_initial_dispatch_is_rejected():

    with pytest.raises(ValueError):
        SchedulerOverhead(initial_dispatch=-10)


def test_negative_context_switch_is_rejected():

    with pytest.raises(ValueError):
        SchedulerOverhead(context_switch=-10)


def test_non_integer_overhead_is_rejected():

    with pytest.raises(ValueError):
        SchedulerOverhead(context_switch=10.5)


def test_boolean_overhead_is_rejected():

    with pytest.raises(ValueError):
        SchedulerOverhead(context_switch=True)


def test_configuration_is_immutable():

    overhead = SchedulerOverhead(100, 50)

    with pytest.raises(AttributeError):
        overhead.context_switch = 200
