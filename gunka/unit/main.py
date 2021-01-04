# -*- coding: utf-8 -*-
"""The highest superstructure of gunka itself."""

###########
# IMPORTS #
###########


# Local:
from gunka.unit.base import BaseUnit
import gunka.pred as pred
import gunka.utils as utils


#############
# INTERFACE #
#############


class Unit(BaseUnit):
    """An encapsulated unit of work ready for cooperative concurrency.

    This class adds some higher-level functionality for convenience.

    """

    def __bool__(self):
        """Represent the unit of work in a Boolean context.

        The unit is considered true if it and its children are all complete
        and succeeded without a noted program error.

        """
        return utils.first(lambda u: not pred.acceptable(u), self) is None
