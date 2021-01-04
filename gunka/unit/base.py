# -*- coding: utf-8 -*-
"""The foundation of gunka."""

###########
# IMPORTS #
###########

# Future:
from __future__ import annotations

# Standard:
from typing import Awaitable
from typing import Callable
from typing import List
import asyncio
import datetime
import inspect


#############
# INTERFACE #
#############


class BaseUnit():
    """An encapsulated unit of work, without abstractions."""

    class State():
        """The state of a unit of work.

        Each instance of this class describes the unit as such, with a focus
        on whether it’s run or not, and roughly what the outcome was.

        This basic version does not track the overall state with a single
        value. An expansion could provide a translation to an Enum or other
        serializable descriptor for such an overall state.

        Properties are updated by the unit.

        """

        def __init__(self, inputs=None):
            """Initialize pessimistically.

            Times of starting and stopping should be timezone-aware UTC
            datetime objects when set, but default to None to indicate that
            the unit has not been started nor stopped.

            Inputs to and outputs from the unit are dicts. The outputs should
            be serializable at all times.

            The remaining properties are Booleans at all times:

            * The ‘cancelled’ property describes whether the work was
              cancelled, in the strict asyncio sense of the word.

            * The ‘error’ property also describes the program of which the unit
              is a part.

            * The ‘failure’ property describes the work itself.

            These properties should only be checked when the unit is complete.
            Their order of precedence is as listed here.

            """
            self.time_started = None
            self.time_stopped = None

            self.inputs = inputs or dict()
            self.outputs = dict()

            self.cancelled = False
            self.error = True       # Deliberate pessimism.
            self.failure = True     # Deliberate pessimism.

    class ConclusionSignal(BaseException):
        """A signal to conclude work.

        In the same way that asyncio.CancelledError inherits from
        BaseException since Python 3.8, ConclusionSignal also inherits from
        BaseException. This has the benefit that it is not easily caught by
        accident in a work function, which would disrupt control flow.

        """

        def __init__(self, error=False, propagate=False):
            """Initialize."""
            self.error = error
            self.propagate = propagate

    def __init__(self, work: Callable[[BaseUnit], Awaitable[None]],
                 **kwargs):
        """Initialize."""
        assert inspect.iscoroutinefunction(work)
        self._work = work
        self.state = self.State(**kwargs)
        self.children: List[BaseUnit] = list()

    def succeed(self, **kwargs):
        """Retire. Note a success, leaving any remaining work undone."""
        self.state.failure = False
        raise self.ConclusionSignal(**kwargs)

    def fail(self, **kwargs):
        """Note a serious problem that is not an internal error."""
        raise self.ConclusionSignal(**kwargs)

    def panic(self):
        """Note an internal error in the program."""
        raise self.ConclusionSignal(error=True, propagate=True)

    def _get_current_time(self):
        """Return the current UTC date and time."""
        return datetime.datetime.now(tz=datetime.timezone.utc)

    async def __call__(self) -> BaseUnit:
        """Perform work. Return self."""
        assert self.state.time_started is None

        try:
            self.state.time_started = self._get_current_time()
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
            self.state.time_stopped = self._get_current_time()

        return self
