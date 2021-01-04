# -*- coding: utf-8 -*-
"""The foundation of gunka."""

###########
# IMPORTS #
###########


# Future:
from __future__ import annotations

# Standard:
from collections.abc import Hashable
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID
import asyncio
import datetime
import inspect


#############
# INTERFACE #
#############


class BaseUnit():
    """An encapsulated unit of work, without abstractions."""

    # Dataclasses defined by this class are intended as minimalistic modules,
    # to be expanded, replaced or ignored by implementers, as needed.

    @dataclass()
    class Identification():
        """The formal identity of a unit of work."""

        application: Optional[UUID] = field(default=None)
        context: Optional[UUID] = field(default=None)
        instance: Optional[UUID] = field(default=None)
        result: Optional[UUID] = field(default=None)

    @dataclass()
    class UserInterface():
        """User-facing descriptions of a unit."""

        title: Optional[str] = field(default=None)
        result: Optional[str] = field(default=None)

    @dataclass()
    class State():
        """The state of a unit of work.

        Each instance of this class describes the unit as such, with a focus
        on whether it’s run or not, and roughly what the outcome was.

        This basic version does not track the overall state with a single
        value. An expansion could provide a translation to an Enum or other
        serializable descriptor for such an overall state.

        Properties are updated by the unit.

        The ‘cancelled’ property describes whether the work was cancelled, in
        the strict asyncio sense of the word.

        The ‘error’ property also describes the program of which the unit is a
        part.

        The ‘failure’ property describes the work itself, not the program.

        These three Boolean properties should only be checked when the unit is
        complete. Their order of precedence is as listed here.

        """

        # Chronological state. Defaults mean neither started nor stopped.
        time_started: Optional[datetime.datetime] = field(default=None)
        time_stopped: Optional[datetime.datetime] = field(default=None)

        # Semantic state.
        inputs: Dict[str, Any] = field(default_factory=dict)
        outputs: Dict[str, Hashable] = field(default_factory=dict)

        # Non-identifying result atoms.
        cancelled: bool = field(default=False)
        error: bool = field(default=True)       # Deliberate pessimism.
        failure: bool = field(default=True)     # Deliberate pessimism.

    class ConclusionSignal(BaseException):
        """A signal to conclude work.

        In the same way that asyncio.CancelledError inherits from
        BaseException since Python 3.8, ConclusionSignal also inherits from
        BaseException. This has the benefit that it is not easily caught by
        accident in a work function, which would disrupt control flow.

        """

        def __init__(self, source: BaseUnit, error=False, propagate=False):
            """Initialize."""
            self.source = source
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
        raise self.ConclusionSignal(self, **kwargs)

    def fail(self, **kwargs):
        """Note a serious problem that is not an internal error."""
        raise self.ConclusionSignal(self, **kwargs)

    def panic(self):
        """Note an internal error in the program."""
        raise self.ConclusionSignal(self, error=True, propagate=True)

    async def __call__(self) -> BaseUnit:
        """Perform work. Return self."""
        assert self.state.time_started is None

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


def get_current_time() -> datetime.datetime:
    """Get the current date and time on the local system.

    This function is defined for the simplification of unit tests, as a
    bare-bones alternative to using a higher-level third-pary library for time.

    """
    return datetime.datetime.now(tz=datetime.timezone.utc)
