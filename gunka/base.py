# -*- coding: utf-8 -*-
"""The foundation of gunka."""

###########
# IMPORTS #
###########


# Standard:
import asyncio
import datetime
import inspect

# Local:
from . import utils
from . import pred


#############
# INTERFACE #
#############


class Unit():
    """An encapsulated unit of work ready for cooperative concurrency."""

    class State():
        """The state of a unit of work.

        Each instance of this class describes the unit as such, with a focus
        on whether it’s run or not, and roughly what the outcome was.

        This basic version does not track the overall state with a single
        value. An expansion could provide a translation to an Enum or other
        serializable descriptor for such an overall state.

        Properties are updated by the unit.

        """

        def __init__(self):
            """Initialize pessimistically.

            Times of starting and stopping should be timezone-aware UTC
            datetime objects when set, but default to None to indicate that
            the unit has not been started nor stopped.

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

            self.cancelled = False
            self.error = True       # Deliberate pessimism.
            self.failure = True     # Deliberate pessimism.

    class ConclusionSignal(Exception):
        """A signal to conclude work."""

        def __init__(self, error=False, propagate=False):
            """Initialize."""
            self.error = error
            self.propagate = propagate

    def __init__(self, work=None, inputs=None):
        """Initialize."""
        assert inspect.iscoroutinefunction(work)
        self._work = work

        self.state = self.State()
        self.inputs = inputs or dict()
        self.outputs = dict()

        self.children = list()

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

    async def __call__(self):
        """Perform work. Return self."""
        assert self.state.time_started is None

        try:
            self.state.time_started = self._get_current_time()
            await self._work(self, **self.inputs)
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

    def __bool__(self):
        """Represent the unit of work in a Boolean context.

        The unit is considered true if it and its children are all complete
        and succeeded without a noted program error.

        """
        return utils.first(lambda u: not pred.acceptable(u), self) is None
