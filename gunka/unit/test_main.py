# -*- coding: utf-8 -*-
"""Unit tests for the main module, using pytest."""

###########
# IMPORTS #
###########


# Standard:
import asyncio

# Local:
from gunka.unit.main import Unit


#########
# TESTS #
#########


def test_boolean_notstarted_false():
    """Check that an unstarted unit is considered false."""
    async def work(unit, **_):
        pass

    unit = Unit(work)
    assert not unit


def test_boolean_noop_true():
    """Check that a started no-op unit is considered true."""
    async def work(unit, **_):
        pass

    unit = Unit(work)
    asyncio.run(unit())

    assert unit.state.time_started
    assert unit.state.time_stopped
    assert not unit.state.failure
    assert unit


def test_concurrency_trivial():
    """Check the work of a parent with two concurrent children."""
    async def pseudochild(unit, key=None, value=None):
        unit.state.outputs[key] = value

    async def parent_work(unit=None):
        await asyncio.gather(pseudochild(unit=unit, key='a', value=1),
                             pseudochild(unit=unit, key='b', value=2))

    unit = Unit(parent_work)
    asyncio.run(unit())

    assert unit
    assert unit.state.outputs == dict(a=1, b=2)


def test_exception_under_gather():
    """Test exception propagation under asyncio.gather.

    This expands upon test_concurrency_trivial. Here, each child is still a
    coroutine, not a separate unit. Each will sleep and then call for its unit
    to fail.

    The expected result is that the first child will complete its work and
    the second child will be cancelled while asleep, because the unit has
    failed.

    """
    async def pseudochild(unit, key=None, value=None):
        unit.state.outputs[f'{key}0'] = value
        await asyncio.sleep(value)
        unit.state.outputs[f'{key}1'] = value
        unit.fail()

    async def parent_work(unit=None):
        await asyncio.gather(pseudochild(unit=unit, key='A', value=0),
                             pseudochild(unit=unit, key='B', value=1))

    unit = Unit(parent_work)
    asyncio.run(unit())

    assert not unit
    assert unit.state.outputs == dict(A0=0, A1=0, B0=1)
