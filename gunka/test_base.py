# -*- coding: utf-8 -*-
"""Unit tests for the base module, using pytest."""

###########
# IMPORTS #
###########


# Standard:
import asyncio

# Local:
from . import base


#########
# TESTS #
#########


def test_boolean_notstarted_false():
    async def work(u, **_):
        pass

    unit = base.Unit(work=work)
    assert not unit


def test_boolean_noop_true():
    async def work(u, **_):
        pass

    unit = base.Unit(work=work)
    asyncio.run(unit())

    assert unit.state.time_started
    assert unit.state.time_stopped
    assert unit.state.success
    assert unit


def test_concurrency_trivial():
    async def child(unit, key=None, value=None):
        unit.outputs[key] = value

    async def parent_work(unit=None):
        asyncio.gather(child(unit=unit, key='a', value=1),
                       child(unit=unit, key='b', value=2))

    unit = base.Unit(work=parent_work)
    asyncio.run(unit())

    assert unit
    assert unit.outputs == dict(a=1, b=2)
