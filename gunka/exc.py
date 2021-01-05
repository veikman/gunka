# -*- coding: utf-8 -*-
"""Basic classes of exceptions."""


class Signal(BaseException):
    """A signal in Gunka’s control flow.

    In the same way that asyncio.CancelledError inherits from BaseException
    (since Python 3.8), Signal also inherits from BaseException. This has the
    benefit that it is not easily caught by accident in a work function, which
    would disrupt control flow.

    """


class ValidationFailure(Exception):
    """An indication that some unit of work has invalid properties.

    This is intended for use when work cannot safely continue as a result of
    Gunka components (scaffolds etc). not having properties defined as required
    for an application, which in turn would be a reliable indication of
    programmer error.

    """
