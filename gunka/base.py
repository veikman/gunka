# -*- coding: utf-8 -*-
"""The foundation of gunka."""

###########
# IMPORTS #
###########


# Standard:
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

        """
        def __init__(self):
            """Initialize pessimistically. Values are updated by the unit.

            Times of starting and stopping should be UTC datetime objects.
            The remaining properties are Booleans at all times.

            The ‘cancelled’ property describes whether work should continue.
            It is intended to serve as the subject of a callback function in
            long-running operations.

            The ‘error’ property describes the program of which the unit
            is a part. It should take precedence over the ‘success’ member,
            which describes the work itself.

            """
            self.time_started = None
            self.time_stopped = None

            self.cancelled = False
            self.error = True       # Deliberate pessimism.
            self.success = False

    class ConclusionSignal(Exception):
        """A signal to conclude work."""
        def __init__(self, error=False, propagate=False):
            self.error = error
            self.propagate = propagate

    def __init__(self, work=None, inputs=None, teardown=lambda: None):
        assert inspect.iscoroutinefunction(work)
        self._work = work
        self._inputs = inputs or dict()
        self._teardown = teardown

        self.state = self.State()
        self.children = list()
        self.outputs = dict()

    def retire(self, **kwargs):
        """Finish early."""
        self.state.success = True
        raise self.ConclusionSignal(**kwargs)

    def panic(self):
        """Note an internal error in the program."""
        raise self.ConclusionSignal(error=True, propagate=True)

    def mark_cancellation(self):
        """Set a flag to call off any further work. Propagate to children.

        This does not immediately halt work.

        """
        self.state.cancelled = True
        for child in self.children:
            child.cancel()

    def _conclude_if_cancelled(self, **kwargs):
        """Check for cancellation. Stop if the cancellation flag is set.

        This should be done periodically in any lengthy unit, in such a way
        that loose ends are minimized.

        """
        if self.state.cancelled:
            raise self.ConclusionSignal(**kwargs)

    async def __call__(self):
        """Perform work."""
        try:
            self._conclude_if_cancelled()
            self.state.time_started = datetime.datetime.utcnow()
            await self._work(self, **self._inputs)
        except self.ConclusionSignal as signal:
            self.state.error = signal.error
            if signal.propagate:
                signal.error = False
                raise
        else:
            self.state.error = False
            self.state.success = True
        finally:
            self.state.time_stopped = datetime.datetime.utcnow()
            self._teardown()
        return self

    def __bool__(self):
        return utils.first(lambda u: not pred.acceptable(u), self) is None
