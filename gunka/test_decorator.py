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


#########
# TESTS #
#########


def test_title_required_omitted():
    note = define_work_decorator(require_title=True)

    with pytest.raises(AssertionError):
        @note()  # Title of unit not specified.
        async def work(unit: Unit):
            pass


def test_title_required_included():
    note = define_work_decorator(require_title=True)

    @note(title='lo tcita ku')
    async def work(unit: Unit):
        pass

    assert work.ui is not None
    assert work.ui.title == 'lo tcita ku'
