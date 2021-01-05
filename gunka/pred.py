# -*- coding: utf-8 -*-
"""Predicate functions for scaffolds and/or units."""

###########
# IMPORTS #
###########


# Standard:
from asyncio import iscoroutinefunction
from uuid import UUID

# Local:
from gunka.unit.base import BaseUnit


#############
# INTERFACE #
#############


def require_coroutine_function(scaffold) -> bool:
    """Check that a work function is a coroutine function."""
    return iscoroutinefunction(scaffold.work)


def require_application_uuid(scaffold) -> bool:
    """Check that a work function is tagged with a unit UUID."""
    return scaffold.id and isinstance(scaffold.id.application, UUID)


def require_title(scaffold) -> bool:
    """Check that a work function is tagged with a default unit title."""
    return scaffold.ui and isinstance(scaffold.ui.title, str)


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
