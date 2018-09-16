# -*- coding: utf-8 -*-
"""Predicate functions for Units."""

#############
# INTERFACE #
#############


def complete(unit):
    """Check whether passed unit is complete."""
    return bool(unit.state.time_started and unit.state.time_stopped)


def nonerror_success(unit):
    """Check whether passed unit succeeded without internal error."""
    return bool((not unit.state.error) and unit.state.success)


def acceptable(unit):
    """Check whether passed unit is OK in a general sense."""
    return bool(complete(unit) and nonerror_success(unit))
