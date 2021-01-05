# -*- coding: utf-8 -*-
"""Unit tests for annotating functions."""

###########
# IMPORTS #
###########


# Third party:
import pytest

# Local:
from gunka.decorator import define_work_decorator
from gunka.unit.main import Unit
from gunka.pred import require_title
from gunka.exc import ValidationFailure


#########
# TESTS #
#########


def test_title_required_omitted():
    """Check omitting a title when a validator requires it."""
    note = define_work_decorator(Unit, validators=(require_title,))

    with pytest.raises(ValidationFailure):
        @note()  # Title of unit required but not specified.
        async def work(unit: Unit):
            pass


def test_title_required_included():
    """Check including a title when a validator requires it."""
    note = define_work_decorator(Unit, validators=(require_title,))

    @note(title='lo tcita ku')
    async def tcita(unit: Unit):
        pass

    assert tcita.ui is not None
    assert tcita.ui.title == 'lo tcita ku'
