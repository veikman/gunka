# -*- coding: utf-8 -*-
"""Predicate functions for Units."""

###########
# IMPORTS #
###########


# Local:
from gunka.unit.base import BaseUnit


#############
# INTERFACE #
#############


def complete(unit: BaseUnit) -> bool:
    """Check whether passed unit is complete."""
    return bool(unit.state.time_started is not None and
                unit.state.time_stopped is not None and
                not unit.state.cancelled)


def nonerror_success(unit: BaseUnit) -> bool:
    """Check whether passed unit succeeded without internal error."""
    return bool((not unit.state.error) and (not unit.state.failure))


def acceptable(unit: BaseUnit) -> bool:
    """Check whether passed unit is OK in a general sense."""
    return bool(complete(unit) and nonerror_success(unit))
