# -*- coding: utf-8 -*-
"""Core function-oriented utilities for working with Units."""

#############
# INTERFACE #
#############


def flatten(unit):
    yield unit
    yield from map(flatten, unit.children)


def first(predicate, unit):
    for u in flatten(unit):
        if predicate(u):
            return u
