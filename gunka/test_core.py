# -*- coding: utf-8 -*-
"""Unit tests for major emergent functionality."""

###########
# IMPORTS #
###########


# Standard:
import asyncio

# Third party:
import pytest

# Local:
from gunka.decorator import permissive
from gunka.unit.main import Unit


#########
# TESTS #
#########


def test_parent_trivial():
    """Check that a unit can easily create and run another."""
    @permissive()
    async def a(unit: Unit):
        pass

    @permissive()
    async def b(unit: Unit):
        await unit.new_child(a)()

    root = Unit(b)
    asyncio.run(root())

    assert root
    assert root._work is b.work

    assert len(root.children) == 1

    assert root.children[0]
    assert root.children[0]._work is a.work


def test_parent_of_success():
    """Check the effect on a family of a child calling succeed().

    The child calling the method should be cut short, but the parent should
    continue thereafter. Both should be truthy when stopped.

    """
    @permissive()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        unit.succeed()
        unit.state.outputs.update(after=True)

    @permissive()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        await unit.new_child(a)()
        unit.state.outputs.update(after=True)

    root = Unit(b)
    asyncio.run(root())

    assert root
    assert root.state.outputs == dict(before=True, after=True)

    assert len(root.children) == 1

    assert root.children[0]
    assert root.children[0].state.outputs == dict(before=True)


def test_parent_of_failure():
    """Check the effect on a family of a child calling fail().

    The child calling the method should be cut short, but the parent should
    continue thereafter. Neither should be truthy when stopped.

    """
    @permissive()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        unit.fail()
        unit.state.outputs.update(after=True)

    @permissive()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        await unit.new_child(a)()
        unit.state.outputs.update(after=True)

    root = Unit(b)
    asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(before=True, after=True)
    assert not root.state.failure
    assert not root.state.error

    assert len(root.children) == 1

    assert not root.children[0]
    assert root.children[0].state.outputs == dict(before=True)
    assert root.children[0].state.failure
    assert not root.children[0].state.error


def test_parent_of_acknowledged_error():
    """Check the effect on a family of a child calling panic().

    The child calling the method should be cut short, and the parent too.
    Neither should be truthy when stopped.

    """
    @permissive()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        unit.panic()
        unit.state.outputs.update(after=True)

    @permissive()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        await unit.new_child(a)()
        unit.state.outputs.update(after=True)

    root = Unit(b)

    with pytest.raises(root.ConclusionSignal):
        asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(before=True)
    assert not root.state.error

    assert len(root.children) == 1

    assert not root.children[0]
    assert root.children[0].state.outputs == dict(before=True)
    assert root.children[0].state.error


def test_parent_of_unacknowledged_uncaught_error():
    """Check the effect on a family of a child dividing by zero.

    The consequences should resemble those of an acknowledged error, but the
    child’s exception propagates directly.

    """
    @permissive()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        1 / 0
        unit.state.outputs.update(after=True)

    @permissive()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        await unit.new_child(a)()
        unit.state.outputs.update(after=True)

    root = Unit(b)

    with pytest.raises(ZeroDivisionError):
        asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(before=True)
    assert root.state.error

    assert len(root.children) == 1

    assert not root.children[0]
    assert root.children[0].state.outputs == dict(before=True)
    assert root.children[0].state.error


def test_parent_of_unacknowledged_caught_error():
    """Check the effect on a family of a child dividing by zero.

    In this variation on the above, the parent anticipates the error.

    """
    @permissive()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        1 / 0
        unit.state.outputs.update(after=True)

    @permissive()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        try:
            await unit.new_child(a)()
        except ZeroDivisionError:
            pass
        unit.state.outputs.update(after=True)

    root = Unit(b)
    asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(before=True, after=True)
    assert not root.state.failure
    assert not root.state.error

    assert len(root.children) == 1

    assert not root.children[0]
    assert root.children[0].state.outputs == dict(before=True)
    assert root.children[0].state.error


def test_concurrency_simple():
    """Check the consequences of well-behaved concurrent children."""
    @permissive()
    async def a(unit: Unit):
        await asyncio.sleep(0.01)

    @permissive()
    async def b(unit: Unit):
        a0 = unit.new_child(a)
        a1 = unit.new_child(a)
        await asyncio.gather(a0(), a1())

    root = Unit(b)
    asyncio.run(root())

    assert root
    assert len(root.children) == 2

    a0, a1 = root.children
    assert a0.state.time_started < a1.state.time_started
    assert a0.state.time_stopped > a1.state.time_started  # Overlap.
    assert a0.state.time_stopped < a1.state.time_stopped


def test_concurrency_with_failure():
    """Check the consequences of a middle child failing."""
    @permissive()
    async def a(unit: Unit):
        await asyncio.sleep(0.01)

    @permissive()
    async def b(unit: Unit):
        unit.fail()

    @permissive()
    async def c(unit: Unit):
        a0 = unit.new_child(a)
        b0 = unit.new_child(b)
        a1 = unit.new_child(a)
        await asyncio.gather(a0(), b0(), a1())
        unit.state.outputs.update(after=True)

    root = Unit(c)
    asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(after=True)
    assert not root.state.failure
    assert not root.state.error

    assert len(root.children) == 3

    assert root.children[0]

    assert not root.children[1]
    assert root.children[1].state.failure
    assert not root.children[1].state.error

    assert root.children[2]
