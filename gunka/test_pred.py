# -*- coding: utf-8 -*-
"""Unit tests for the pred module, using pytest."""

###########
# IMPORTS #
###########


# Standard:
import datetime
from unittest import mock

# 3rd party:
import pytest

# Local:
from . import base
from . import pred


#########
# TESTS #
#########


@pytest.fixture()
def sou():
    """Create a fake state-only unit (SOU) as a fixture."""
    obj = mock.Mock()
    obj.state = base.Unit.State()
    obj.seal()
    return obj


def test_complete(sou):
    """Exercise the “complete” predicate."""
    # Gradually populate the state.
    assert not pred.complete(sou)
    sou.state.time_started = datetime.datetime.utcnow()
    assert not pred.complete(sou)
    sou.state.time_stopped = datetime.datetime.utcnow()
    assert pred.complete(sou)

    # Unset a time. This should never happen in real-world use.
    sou.state.time_started = None
    assert not pred.complete(sou)


def test_nonerror_success(sou):
    """Exercise the “nonerror_success” predicate."""
    # Gradually populate the state.
    assert not pred.nonerror_success(sou)
    sou.state.error = False
    assert not pred.nonerror_success(sou)
    sou.state.failure = False
    assert pred.nonerror_success(sou)

    # Reset the error flag. This should never happen in real-world use.
    sou.state.error = True
    assert not pred.nonerror_success(sou)


def test_acceptable_true(monkeypatch, sou):
    """Check that the “acceptable” predicate clears a patched-over SOU."""
    monkeypatch.setattr(pred, 'complete', lambda _: True)
    monkeypatch.setattr(pred, 'nonerror_success', lambda _: True)
    assert pred.acceptable(sou)


def test_acceptable_false_incomplete(monkeypatch, sou):
    """Check that the “acceptable” predicate requires completeness."""
    monkeypatch.setattr(pred, 'complete', lambda _: False)
    monkeypatch.setattr(pred, 'nonerror_success', lambda _: True)
    assert not pred.acceptable(sou)


def test_acceptable_false_failure(monkeypatch, sou):
    """Check that the “acceptable” predicate requires a non-error success."""
    monkeypatch.setattr(pred, 'complete', lambda _: True)
    monkeypatch.setattr(pred, 'nonerror_success', lambda _: False)
    assert not pred.acceptable(sou)
