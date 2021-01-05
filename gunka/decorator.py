# -*- coding: utf-8 -*-
"""Conveniences for annotating work functions for units of work."""

##########
# IMPORT #
##########


# Standard:
from asyncio import iscoroutinefunction
from typing import Optional
from typing import Type
from uuid import UUID

# Local:
from gunka.unit.main import Unit


#############
# INTERFACE #
#############


def define_work_decorator(unit_type: Type[Unit],
                          always_annotate_with_id=False,
                          always_annotate_with_ui=False,
                          require_title=False,
                          require_application_uuid=False):
    """Define a means of annotating work functions."""
    class_id = unit_type.Identification
    class_ui = unit_type.UserInterface

    def work_decorator(uuid_application: Optional[UUID] = None,
                       title: Optional[str] = None,
                       ):
        """Take metadata for a decorator of work functions."""
        annotate_with_id = always_annotate_with_id
        if require_application_uuid:
            annotate_with_id = True
            assert isinstance(uuid_application, UUID)

        annotate_with_ui = always_annotate_with_ui
        if require_title:
            annotate_with_ui = True
            assert isinstance(title, str)

        def get_scaffold(work):
            """Get a scaffold for making units.

            Take a work function. Return a scaffold that stores a reference to
            that work function, along with other metadata for initializing a
            unit to encapsulate the work.

            """
            assert iscoroutinefunction(work)
            scaffold = unit_type.Scaffold(work=work)

            if annotate_with_id:
                scaffold.id = class_id(application=uuid_application)

            if annotate_with_ui:
                scaffold.ui = class_ui(title=title)

            return scaffold

        return get_scaffold

    return work_decorator
