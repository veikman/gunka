# -*- coding: utf-8 -*-
"""The foundation of gunka."""

###########
# IMPORTS #
###########


# Standard:
from collections.abc import Hashable
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID
import datetime


#############
# INTERFACE #
#############


class BaseUnit():
    """An encapsulated unit of work, without abstractions.

    BaseUnit is intended to serve as the base class of live, executable units
    as well as historical units recovered from storage.

    """

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

    def __init__(self):
        """Initialize."""
        self._work = None
        self.state = self.State()
        self.children: List[type(self)] = list()
