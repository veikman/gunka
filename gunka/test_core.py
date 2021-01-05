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
from gunka.decorator import define_work_decorator
from gunka.unit.main import Unit


############
# FIXTURES #
############


@pytest.fixture
def scaffold():
    """Provide a lax decorator for work functions."""
    yield define_work_decorator(Unit)


#########
# TESTS #
#########


def test_parent_trivial(scaffold):
    """Check that a unit can easily create and run another."""
    @scaffold()
    async def a(unit: Unit):
        pass

    @scaffold()
    async def b(unit: Unit):
        await unit.new_child(a)()

    root = Unit(b)
    asyncio.run(root())

    assert root
    assert root._work is b.work

    assert len(root.children) == 1

    assert root.children[0]
    assert root.children[0]._work is a.work


def test_parent_of_success(scaffold):
    """Check the effect on a family of a child calling succeed().

    The child calling the method should be cut short, but the parent should
    continue thereafter. Both should be truthy when stopped.

    """
    @scaffold()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        unit.succeed()
        unit.state.outputs.update(after=True)

    @scaffold()
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


def test_parent_of_failure(scaffold):
    """Check the effect on a family of a child calling fail().

    The child calling the method should be cut short, but the parent should
    continue thereafter. Neither should be truthy when stopped.

    """
    @scaffold()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        unit.fail()
        unit.state.outputs.update(after=True)

    @scaffold()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        await unit.new_child(a)()
        unit.state.outputs.update(after=True)

    root = Unit(b)
    asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(before=True, after=True)
    assert root.children[0].state.failure
    assert not root.children[0].state.error

    assert len(root.children) == 1

    assert not root.children[0]
    assert root.children[0].state.outputs == dict(before=True)
    assert root.children[0].state.failure
    assert not root.children[0].state.error


def test_parent_of_error(scaffold):
    """Check the effect on a family of a child calling panic().

    The child calling the method should be cut short, and the parent too.
    Neither should be truthy when stopped.

    """
    @scaffold()
    async def a(unit: Unit):
        unit.state.outputs.update(before=True)
        unit.panic()
        unit.state.outputs.update(after=True)

    @scaffold()
    async def b(unit: Unit):
        unit.state.outputs.update(before=True)
        await unit.new_child(a)()
        unit.state.outputs.update(after=True)

    root = Unit(b)

    with pytest.raises(root.ConclusionSignal):
        asyncio.run(root())

    assert not root
    assert root.state.outputs == dict(before=True)
    assert root.children[0].state.error

    assert len(root.children) == 1

    assert not root.children[0]
    assert root.children[0].state.outputs == dict(before=True)
    assert root.children[0].state.error
