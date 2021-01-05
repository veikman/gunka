# -*- coding: utf-8 -*-
"""Conveniences for raising scaffolding."""

##########
# IMPORT #
##########


# Standard:
from typing import Any
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import Type
from uuid import UUID

# Local:
from gunka.exc import ValidationFailure
from gunka.unit.main import Unit


#############
# INTERFACE #
#############


def define_work_decorator(unit_type: Type[Unit],
                          always_annotate_with_id=False,
                          always_annotate_with_ui=False,
                          validators: Tuple[Callable[[Any], bool], ...] = (),
                          ):
    """Define a means of annotating work functions.

    Using validators passed to this function, the readiness of a work function
    can be assessed at time of definition, before a unit is created from it.

    """
    class_id = unit_type.Identification
    class_ui = unit_type.UserInterface

    def work_decorator(uuid_application: Optional[UUID] = None,
                       title: Optional[str] = None,
                       ):
        """Take metadata for a decorator of work functions."""
        annotate_with_id = always_annotate_with_id or uuid_application
        annotate_with_ui = always_annotate_with_ui or title

        def get_scaffold(work):
            """Get a scaffold for making units.

            Take a work function. Return a scaffold that stores a reference to
            that work function, along with other metadata for initializing a
            unit to encapsulate the work.

            Validate the scaffold.

            """
            scaffold = unit_type.Scaffold(work=work)

            if annotate_with_id:
                scaffold.id = class_id(application=uuid_application)

            if annotate_with_ui:
                scaffold.ui = class_ui(title=title)

            for validator in validators:
                if not validator(scaffold):
                    s = 'Work function not prepared for unit.'
                    raise ValidationFailure(s)

            return scaffold

        return get_scaffold

    return work_decorator


permissive = define_work_decorator(Unit)
