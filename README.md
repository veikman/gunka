## Gunka

This library is used to delimit and name the individual steps of any piece of
work. It’s named after the Lojban word for work.

Gunka is intended to provide an intermediate level of abstraction in large
applications, where the end user won’t be interested in the smallest details
but will want to observe progress and identify problem areas.

This sort of thing is naturally useful under a GUI in, for example, test tools
and system administration. However, Gunka on its own is not a TUI or GUI. It
handles only the encapsulation of each unit of work.

### Work in progress

Gunka is in a pre-alpha stage. An even earlier draft used Trio for concurrency,
but the current plan is to use the standard asyncio library.

### Design goals

* Procedures are unary functions. No need for one class per step.
* Units can be arbitrarily nested. You don’t have to follow a flat recipe
  structure.
* Your user interface can show, in non-technical terms, what your program is
  doing for the user.
* Non-fatal problems are neatly contained and easy to highlight, while
  fatal problems will propagate.
* Excellent performance through coöperative concurrency.
* Logging of work and its output is easy, in real time and in retrospect.
* Statistical analysis is supported via UUID tagging.

### Installation

Gunka is a regular Python 3 package with an optional, trivial Debian
build target. Refer to the included Makefile.

### Legal

To contact the author, please use the following information:

    Viktor Eikman
    viktor.eikman@gmail.com
    Grevegårdsvägen 164, 42161 Västra Frölunda, SWEDEN

Please submit your contribution to this project for review.

Gunka is licensed as detailed in the accompanying file COPYING.txt.
