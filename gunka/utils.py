# -*- coding: utf-8 -*-
"""Core function-oriented utilities for working with Units."""

###########
# IMPORTS #
###########


# Standard:
from typing import Callable
from typing import Iterable
from typing import Optional

# Local:
from gunka.unit.base import BaseUnit


#############
# INTERFACE #
#############


def flatten(unit: BaseUnit) -> Iterable[BaseUnit]:
    """Generate the passed unit and its family tree in one flat stream.

    This is preorder tree traversal.

    """
    yield unit
    yield from map(flatten, unit.children)


def first(predicate: Callable[[BaseUnit], bool], unit: BaseUnit
          ) -> Optional[BaseUnit]:
    """Apply the passed predicate function to the passed unit and its family.

    Return the first unit in the family that matches the predicate, if any,
    else return None.

    """
    for u in flatten(unit):
        if predicate(u):
            return u
    return None
