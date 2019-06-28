# -*- coding: utf-8 -*-
"""Core function-oriented utilities for working with Units."""

#############
# INTERFACE #
#############


def flatten(unit):
    """Generate the passed unit and its family tree in one flat stream."""
    yield unit
    yield from map(flatten, unit.children)


def first(predicate, unit):
    """Apply the passed predicate function to the passed unit and its family.

    Return the first unit in the family that matches the predicate, if any,
    else return None.

    """
    for u in flatten(unit):
        if predicate(u):
            return u
