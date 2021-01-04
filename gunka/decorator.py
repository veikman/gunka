# -*- coding: utf-8 -*-
"""Conveniences for annotating work functions for units of work."""

##########
# IMPORT #
##########


# Standard:
from typing import Optional
from uuid import UUID

# Local:
from gunka.unit.base import BaseUnit


#############
# INTERFACE #
#############


def define_work_decorator(always_annotate_with_id=False,
                          always_annotate_with_ui=False,
                          class_id=BaseUnit.Identification,
                          class_ui=BaseUnit.UserInterface,
                          require_title=False,
                          require_application_uuid=False):
    """Define a means of annotating work functions."""
    def work_decorator(uuid_application: Optional[UUID] = None,
                       title: Optional[str] = None,
                       ):
        """Take metadata for a decorator of work functions."""
        annotate_with_id = always_annotate_with_id
        if require_application_uuid:
            annotate_with_id = True
            assert isinstance(uuid_application, str)

        annotate_with_ui = always_annotate_with_ui
        if require_title:
            annotate_with_ui = True
            assert isinstance(title, str)

        def annotate(work):
            """Annotate a work function."""
            if annotate_with_ui:
                work.ui = class_ui(title=title)

            if annotate_with_id:
                work.id = class_id(application=uuid_application)

            return work

        return annotate

    return work_decorator
