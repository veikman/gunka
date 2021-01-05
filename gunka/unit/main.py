# -*- coding: utf-8 -*-
"""The main infrastructure of Gunka’s control flow."""

###########
# IMPORTS #
###########


# Future:
from __future__ import annotations

# Standard:
from copy import deepcopy
from dataclasses import field
from dataclasses import make_dataclass
from dataclasses import replace
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Type
import asyncio
import datetime
import inspect

# Local:
from gunka.exc import Signal
from gunka.unit.base import BaseUnit
import gunka.pred as pred
import gunka.utils as utils


#######################
# INTERFACE FUNCTIONS #
#######################


def get_current_time() -> datetime.datetime:
    """Get the current date and time on the local system.

    This function is defined and exposed for the simplification of unit tests,
    as a bare-bones alternative to using a higher-level, more easily patched
    third-party library for time.

    """
    return datetime.datetime.now(tz=datetime.timezone.utc)


def has_scaffold(cls: Type[Unit]):
    """Annotate a new class of unit with a scaffold for instantiating it."""
    cls.Scaffold = make_dataclass(
        'Scaffold',
        [('work', Callable[[cls], Awaitable[None]]),
         ('id', Optional[cls.Identification], field(default=None)),
         ('ui', Optional[cls.UserInterface], field(default=None)),
         ],
    )
    return cls


#####################
# INTERFACE CLASSES #
#####################


@has_scaffold
class Unit(BaseUnit):
    """An encapsulated unit of work ready for cooperative concurrency.

    This class adds support for execution and some higher-level functionality
    for convenience.

    """

    class ConclusionSignal(Signal):
        """A signal to conclude work."""

        def __init__(self, source: Unit, error=False, propagate=False):
            """Initialize."""
            self.source = source
            self.error = error
            self.propagate = propagate

    # Refer to the has_scaffold function.
    Scaffold: Type

    def __init__(self, scaffold):
        assert isinstance(scaffold, self.Scaffold)
        super().__init__()

        self._work = scaffold.work

        if scaffold.id is not None:
            self.id = replace(scaffold.id)

        if scaffold.ui is not None:
            self.ui = replace(scaffold.ui)

    def new_child(self, scaffold,
                  cls: Type[Unit] = None,
                  copy_inputs: bool = True,
                  new_inputs: Dict[str, Any] = None,
                  ):
        """Create and register a new child unit of self."""
        # TODO: Convenient support for context UUID.
        # TODO: Convenient support for a title other than the scaffold’s.
        if cls is None:
            cls = type(self)

        child = cls(scaffold)

        if copy_inputs:
            child.state.inputs = deepcopy(self.state.inputs)

        if new_inputs is not None:
            child.state.inputs.update(new_inputs)

        self.children.append(child)

        return child

    def succeed(self, **kwargs):
        """Retire. Note a success, leaving any remaining work undone."""
        self.state.failure = False
        raise self.ConclusionSignal(self, **kwargs)

    def fail(self, **kwargs):
        """Note a serious problem that is not an internal error."""
        raise self.ConclusionSignal(self, **kwargs)

    def panic(self):
        """Note an internal error in the program."""
        raise self.ConclusionSignal(self, error=True, propagate=True)

    async def __call__(self) -> Unit:
        """Perform work. Return self."""
        assert self.state.time_started is None
        assert inspect.iscoroutinefunction(self._work)

        try:
            self.state.time_started = get_current_time()
            await self._work(self)
        except asyncio.CancelledError:
            self.state.cancelled = True
            raise  # Propagated for signalling.
        except self.ConclusionSignal as signal:
            self.state.error = signal.error
            if signal.propagate:
                signal.error = False
                raise
        else:
            # Work passed without incident: No known error or failure occurred.
            self.state.error = False
            self.state.failure = False
        finally:
            self.state.time_stopped = get_current_time()

        return self

    def __bool__(self):
        """Represent the unit of work in a Boolean context.

        The unit is considered true if it and its children are all complete
        and succeeded without a noted program error.

        """
        return utils.first(lambda u: not pred.acceptable(u), self) is None
